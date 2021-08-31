"""
TBD
"""

__author__ = "Lukas Mahler"
__version__ = "2.0.0"
__date__ = "31.08.2021"
__email__ = "m@hler.eu"
__status__ = "Development"

# Imports
import platform
import colorama
from termcolor import colored
import alarm
import os
import time
import subprocess
import logging
import configparser
import threading
import msvcrt  # Windows only!


def readCFG(filename):
    wdir = os.path.dirname(os.path.realpath(__file__))
    iniVar = {}

    # Config Laden
    with open(wdir + "\\" + filename) as ini:
        config = configparser.RawConfigParser(allow_no_value=True)
        config.read_file(ini)

    for section in config.sections():
        key = section
        opt = {}
        for options in config.options(section):
            y = {options: config.get(section, options)}
            opt.update(y)
        x = {key: opt}
        iniVar.update(x)

    return iniVar


def currT():
    t = time.strftime("%H:%M:%S")
    return t


def getRAM():
    ram_avail = 0
    ram_info_avail = subprocess.check_output('WMIC memorychip get capacity', shell=True).decode("utf-8").split()
    ram_info_free = subprocess.check_output('WMIC OS get FreePhysicalMemory /Value', shell=True).decode("utf-8").split("=")
    del ram_info_avail[0]
    del ram_info_free[0]
    ram_info_free = str(ram_info_free[0])
    ram_info_free = ram_info_free.replace("\n", "")
    ram_info_free = int(ram_info_free.replace("\r", ""))
    riegel = len(ram_info_avail)
    for r in ram_info_avail:
        ram_avail = ram_avail + int(r)
    ram_avail = round(ram_avail / 1000000000, 2)  # MBIT o. MBYTE?
    ram_avail = "{:5.2f}".format(ram_avail)
    ram_free = round(ram_info_free / 1000000, 2)  # MBIT o. MBYTE?
    ram_free = "{:5.2f}".format(ram_free)
    global ram_used
    ram_used = round(float(ram_avail) - float(ram_free), 2)
    ram_used = "{:5.2f}".format(ram_used)
    ram_per_r = round(float(ram_avail) / riegel, 2)
    ram_per_r = "{:5.2f}".format(ram_per_r)

    return riegel, ram_avail, ram_per_r, ram_free, ram_used


def getProc():
    # Prozesse auslesen aus WMIC
    proc = subprocess.check_output('wmic process get name,workingsetsize').decode("utf-8").rstrip().split("\n")
    del proc[0]
    for n in range(len(proc)):
        try:
            tmp = proc[n].split()
            name = " ".join(tmp[:-1])
            size = tmp[-1]
            proc[n] = [name, size]
        except Exception as e:
            continue

    # Umwandeln der Bytes von Str to Int zum Sortieren
    for item in proc:
        try:
            item[1] = int(item[1])
            item[1] = round(item[1] / 1000000, 0)
        except Exception as e:
            item[1] = 0
            continue

    # Entferne leere Listeneinträge
    proc_clean = []
    proc_filtr = filter(None, proc)
    for item in proc_filtr:
        proc_clean.append(item)

    # Zähle Prozesse, berechne durchschnitt
    proc_num = len(proc_clean)
    proc_avrg = int(round((float(ram_used) / proc_num) * 1000, 0))

    # TODO
    # Addieren der Gleichnamigen Prozesse
    # proc_add =

    # Sortiere nach Verbrauch
    rsc = sorted(proc_clean, key=lambda x: x[1], reverse=True)

    # Suche Max Length der Prozessnamen für Anzeigeformatierung
    rsc_len = 0
    for n in range(0, 3):
        temp = len(rsc[n][0])
        if temp > rsc_len:
            rsc_len = temp

    rsc_1 = rsc[0]
    rsc_1 = "{0: <{2}} verbraucht: ~ [{1:4.0f}] MB".format(rsc_1[0], rsc_1[1], rsc_len)
    rsc_2 = rsc[1]
    rsc_2 = "{0: <{2}} verbraucht: ~ [{1:4.0f}] MB".format(rsc_2[0], rsc_2[1], rsc_len)
    rsc_3 = rsc[2]
    rsc_3 = "{0: <{2}} verbraucht: ~ [{1:4.0f}] MB".format(rsc_3[0], rsc_3[1], rsc_len)

    return proc_num, proc_avrg, rsc_1, rsc_2, rsc_3


def getSpace():
    # Freier Festplatten Speicher
    temp = []
    tfix = []

    command = 'wmic logicaldisk get deviceid, freespace, size /VALUE'
    space = subprocess.check_output(command, shell=True).decode("utf-8").split()  # providername = \\172.xxxx
    num = 0
    for item in space:
        item = item.split("=")
        if num != 0:
            if num % 3 == 0:
                temp.append(tfix)
                tfix = [item]
            else:
                tfix.append(item)
        else:
            tfix.append(item)
        num += 1

    del tfix
    tfix = []

    # Wandle Str to Int
    for item in temp:
        if item[1][1] == "":
            del item[1]
            continue
        else:
            try:
                item[1][1] = int(item[1][1])
                item[1][1] = item[1][1] / 1000000000
                item[1][1] = round(item[1][1], 2)
                # --
                item[2][1] = int(item[2][1])
                item[2][1] = item[2][1] / 1000000000
                item[2][1] = round(item[2][1], 2)

                if item[2][1] < item[1][1]:
                    del item
                    continue
                else:
                    pass
            except Exception as e:
                print(e)

        tfix.append(item)

    del temp
    return tfix


def raiseAlarm(cause):
    let = alarm.lastexectime
    alarm.raiseAlarm(cause, let)


def visualize(ram, proc, space):
    red = 'red'
    green = 'green'
    yellow = 'yellow'
    cyan = 'cyan'
    spacer = 120 * "="

    #####################################################################################
    os.system("CLS")
    cdate = time.strftime("%d.%m.%Y")
    print("------------------")
    print("Date:", colored(cdate, cyan), "|")
    print("Time:", colored(currT(), cyan), "  |")
    print("------------------")
    print("")
    #####################################################################################
    if ram[0] >= 2:
        print("Im Computer sind [" + colored(str(ram[0]), green) + "] Ram-Riegel eingebaut!")
    else:
        print("Im Computer ist [" + colored(str(ram[0]), red) + "] Ram-Riegel eingebaut!" +
              colored("												 WARNING: THIS MAY SLOW DOWN YOUR PC", red))
        raiseAlarm("There is only one memory module build in this Computer, this potentially needs fixing.")
    print(spacer)
    if float(ram[1]) >= 8:
        print("Gesamtkapazität   : [" + colored(str(ram[1]), green) + "] GB")
    else:
        print("Gesamtkapazität   : [" + colored(str(ram[1]), red) + "] GB" +
              colored("                                              WARNING: THIS MAY SLOW DOWN YOUR PC", red))
        raiseAlarm("There is less then 4GB of RAM build into this Computer, this potentially needs fixing.")
    if float(ram[2]) >= 4:
        print("Ram pro Riegel    : [" + colored(str(ram[2]), green) + "] GB")
    else:
        print("Ram pro Riegel    : [" + colored(str(ram[2]), red) + "] GB")
    print("------------------------------")
    if float(ram[3]) >= float(ram[1]) * 0.5:
        print("Kapazität frei    : [" + colored(str(ram[3]), green) + "] GB")
        print("Kapazität benutzt : [" + colored(str(ram[4]), green) + "] GB")
    elif float(ram[3]) >= float(ram[1]) * 0.3:
        print("Kapazität frei    : [" + colored(str(ram[3]), yellow) + "] GB" + colored(
            "                                                        WARNING: QUOTA BELOW 50 PERCENT", yellow))
        print("Kapazität benutzt : [" + colored(str(ram[4]), yellow) + "] GB")
        # log.warning("The QUOTA of the RAM is below 50%")
        raiseAlarm("The Quota of the RAM is below 50%, this potentially needs fixing.")
    elif float(ram[3]) < float(ram[1]) * 0.3:
        print("Kapazität frei    : [" + colored(str(ram[3]), red) + "] GB" + colored(
            "                                                        WARNING: QUOTA BELOW 30%", red))
        print("Kapazität benutzt : [" + colored(str(ram[4]), red) + "] GB")
        # log.warning("The QUOTA of the RAM is below 30%")
        raiseAlarm("The Quota of the RAM is below 30%, this needs fixing.")
    print(spacer)
    #####################################################################################
    if proc[0] <= 100:
        print("Es laufen momentan [" + colored(str(proc[0]), green) + "] Prozesse.")
    elif proc[0] > 200:
        print("Es laufen momentan [" + colored(str(proc[0]), yellow) + "] Prozesse." + colored(
            "                                                        WARNING: THRESHOLD EXCEEDED", yellow))
        raiseAlarm("There are more then 200 Processes running, this potentially needs fixing.")
    elif proc[0] > 300:
        print("Es laufen momentan [" + colored(str(proc[0]), red) + "] Prozesse." + colored(
            "                                                        WARNING: THRESHOLD EXCEEDED", red))
        raiseAlarm("There are more then 300 Processes running, this quite surely needs fixing.")
    print(spacer)
    print("Ein Prozess verbraucht durchschnittlich [" + colored(str(proc[1]), cyan) + "] MB")
    print("-----------------------------------------------------")
    print("Die drei Ressource intensivsten Prozesse sind:")
    print("1. ->", proc[2])
    print("2. ->", proc[3])
    print("3. ->", proc[4])
    print(spacer)
    #####################################################################################
    print("")
    print("Alle Internen Festplatten")
    print(spacer)
    for item in space:
        usd = item[2][1] - item[1][1]
        print("Driveletter: [{0: <2}] | Size: [{1:4.0f}] GB | Free: [{2:6.1f}] GB | Used: [{3:6.1f}] GB".format(
            item[0][1], item[2][1], item[1][1], usd))
    print(spacer)
    print("\nPress [q] to quit ", end="")


def setupLogger():
    global log
    log = logging.getLogger()
    handler = logging.FileHandler(f"AllEye v.{__version__}.log")
    logformat = logging.Formatter("%(asctime)s %(levelname)s %(message)s", "%d-%m-%Y %H:%M:%S")
    handler.setFormatter(logformat)
    log.addHandler(handler)
    log.setLevel(logging.DEBUG)

    log.info(f"--------------- AllEye v.{__version__}{__date__} Log ---------------")


def setupCMD():
    colorama.init()

    # start the Keyboard thread
    kthread = KeyboardThread(mycallback)

    # Current Terminal Size
    y = os.get_terminal_size().lines
    x = os.get_terminal_size().columns

    os.system("mode 120,60")

    return x, y


def resetCMD(x, y):
    os.system(f"mode {x},{y}")


def checkOS():
    thisOS = platform.platform()
    if not thisOS.startswith("Windows"):
        raise AssertionError(f"This Tool only works on Windows Systems.\n You seem to be on {thisOS}")


class KeyboardThread(threading.Thread):

    def __init__(self, input_cbk=None, name='keyboard-input-thread'):
        self.input_cbk = input_cbk
        super(KeyboardThread, self).__init__(name=name)
        self.start()

    def run(self):
        while True:
            self.input_cbk(input()) #waits to get input + return


def mycallback(inp):
    if inp.upper() == "Q":
        os._exit(1)


def main():

    checkOS()
    global prex, prey
    prex, prey = setupCMD()
    setupLogger()

    iniVar = readCFG('Settings.ini')
    alarm.refresh()

    done = False
    while not done:

        time.sleep(0.3)
        try:
            ram = getRAM()
            proc = getProc()
            space = getSpace()
            visualize(ram, proc, space)

        except Exception as e:
            log.error(str(e))

    resetCMD(prex, prey)


if __name__ == "__main__":
    main()
