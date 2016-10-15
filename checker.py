# checker.py

from colorama import init
from termcolor import colored
init()
import alarm
import os
import sys
import time
import subprocess
import logging
import configparser

version = "1.2"
versiondate = " (15.10.2016)"

log = logging.getLogger()
handler = logging.FileHandler('AllEye v.'+version+'.log')
format = logging.Formatter('%(asctime)s %(levelname)s %(message)s',		"%d-%m-%Y %H:%M:%S")
handler.setFormatter(format)
log.addHandler(handler) 
log.setLevel(logging.DEBUG)

def readCFG(filename):
	wDir = os.path.dirname(os.path.realpath(__file__))
	iniVar = {}
	
	# Config Laden
	with open(wDir+"\\"+filename) as ini:
		config = configparser.RawConfigParser(allow_no_value=True)
		config.read_file(ini)
	
	for section in config.sections():
		key = section
		opt = {}
		for options in config.options(section):
			y = {options : config.get(section, options)}
			opt.update(y)
		x = {key : opt}
		iniVar.update(x)

	return iniVar

def currT():
	t = time.strftime("%H:%M:%S")
	return t

def getRAM():
	ram_avail = 0
	ram_free = 0
	ram_info_avail = subprocess.check_output('WMIC memorychip get capacity', shell=True).decode("utf-8").split()
	ram_info_free  = subprocess.check_output('WMIC OS get FreePhysicalMemory /Value', shell=True).decode("utf-8").split("=")
	del ram_info_avail[0]
	del ram_info_free[0]
	ram_info_free = str(ram_info_free[0])
	ram_info_free = ram_info_free.replace("\n", "")
	ram_info_free = int(ram_info_free.replace("\r", ""))
	riegel = len(ram_info_avail)
	for r in ram_info_avail:
		ram_avail = ram_avail + int(r)
	ram_avail = round(ram_avail / 1000000000,2)           #MBIT o. MBYTE?
	ram_avail = "{:5.2f}".format(ram_avail)
	ram_free = round(ram_info_free / 1000000,2)			  #MBIT o. MBYTE?
	ram_free = "{:5.2f}".format(ram_free)
	global ram_used
	ram_used = round(float(ram_avail) - float(ram_free),2)
	ram_used = "{:5.2f}".format(ram_used)
	ram_per_r = round(float(ram_avail) / riegel,2)
	ram_per_r = "{:5.2f}".format(ram_per_r)
	
	return riegel,ram_avail,ram_per_r,ram_free,ram_used
	
def getProc():
	##### Prozesse auslesen aus WMIC
	proc = subprocess.check_output('wmic process get name,workingsetsize').decode("utf-8").split("\n")
	del proc[0]
	for n in range(len(proc)):
		proc[n] = proc[n].split()
	proc[0] = [proc[0][0]+" "+proc[0][1]+" "+proc[0][2],proc[0][3]]
	
	##### Umwandeln der Bytes von Str to Int zum Sortieren
	for item in proc:
		try:
			item[1] = int(item[1])
			item[1] = round(item[1] / 1000000,0)
			
		except:
			continue
	
	##### Entferne leere Listeneinträge
	proc_clean = []
	proc_filtr = filter(None, proc)
	for item in proc_filtr:
		proc_clean.append(item)
	
	##### Zähle Prozesse, berechne durchschnitt
	proc_num = len(proc_clean)
	proc_avrg = int(round((float(ram_used) / proc_num)*1000,0))
	
	##### Addieren der Gleichnamigen Prozesse
	#proc_add = 
		
	##### Sortiere nach Verbrauch
	rsc   = sorted(proc_clean,key=lambda x: x[1], reverse=True)
	rsc_len = 0
	for N in range(0,3):
		temp = len(rsc[N][0])
		if temp > rsc_len:
			rsc_len = temp
	
	rsc_1 = rsc[0]
	rsc_1 = "{0: <{2}} verbraucht: ~ [{1:4.0f}] MB".format(rsc_1[0],rsc_1[1],rsc_len)
	rsc_2 = rsc[1]
	rsc_2 = "{0: <{2}} verbraucht: ~ [{1:4.0f}] MB".format(rsc_2[0],rsc_2[1],rsc_len)
	rsc_3 = rsc[2]
	rsc_3 = "{0: <{2}} verbraucht: ~ [{1:4.0f}] MB".format(rsc_3[0],rsc_3[1],rsc_len)
	
	return proc_num,proc_avrg,rsc_1,rsc_2,rsc_3
	
def getSpace():
	
	##### Freier Festplatten Speicher
	temp = []
	tfix = []
	
	space = subprocess.check_output('wmic logicaldisk get deviceid, freespace, size /VALUE', shell=True).decode("utf-8").split()
	num = 0
	for item in space:
		item = item.split("=")
		if num != 0:
			if num % 3 == 0:
				temp.append(tfix)
				tfix = []
				tfix.append(item)
			else:
				tfix.append(item)
		else:
			tfix.append(item)
		num += 1
	
	del tfix
	tfix = []
	
	##### Wandle Str to Int
	for item in temp:
		if item[1][1] == "":
			del item[1]
			continue
		else:
			try:
				item[1][1] = int(item[1][1])
				item[1][1] = item[1][1] / 1000000000
				item[1][1] = round(item[1][1],2)
				#--
				item[2][1] = int(item[2][1])
				item[2][1] = item[2][1] / 1000000000
				item[2][1] = round(item[2][1],2)
				
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

#def triggerWarning(warn):
	
	
def visualize(ram,proc,space):

	red = 'red'
	green = 'green'
	yellow = 'yellow'
	cyan = 'cyan'
	
	#####################################################################################
	os.system("CLS")
	date = time.strftime("%d.%m.%Y")
	print("------------------")
	print("Date:",colored(date,cyan),"|")
	print("Time:",colored(currT(),cyan),"  |")
	print("------------------")
	print("")
	#####################################################################################
	if ram[0] >= 2:
		print("Im Computer sind ["+colored(str(ram[0]),green)+"] Ram-Riegel eingebaut!")
	else:
		print("Im Computer ist ["+colored(str(ram[0]),red)+"] Ram-Riegel eingebaut!"+colored("                                           WARNING: THIS MAY SLOW DOWN YOUR PC",red))
	print("=======================================================================================================================")
	if float(ram[1]) >= 8:
		print("Gesamtkapazität   : ["+colored(str(ram[1]),green)+"] GB")
	else:
		print("Gesamtkapazität   : ["+colored(str(ram[1]),red)+"] GB"+colored("                                                      WARNING: THIS MAY SLOW DOWN YOUR PC",red))
	if float(ram[2]) >= 4:
		print("Ram pro Riegel    : ["+colored(str(ram[2]),green)+"] GB")
	else:
		print("Ram pro Riegel    : ["+colored(str(ram[2]),red)+"] GB")
	print("------------------------------")
	if float(ram[3]) >= float(ram[1])*0.5:
		print("Kapazität frei    : ["+colored(str(ram[3]),green)+"] GB")
		print("Kapazität benutzt : ["+colored(str(ram[4]),green)+"] GB")
	elif float(ram[3]) >= float(ram[1])*0.3:
		print("Kapazität frei    : ["+colored(str(ram[3]),yellow)+"] GB"+colored("                                                      WARNING: QUOTA BELOW 50 PERCENT",yellow))
		print("Kapazität benutzt : ["+colored(str(ram[4]),yellow)+"] GB")
		#log.warning("The QUOTA of the RAM is below 30%")
	elif float(ram[3]) < float(ram[1])*0.3:
		print("Kapazität frei    : ["+colored(str(ram[3]),red)+"] GB"+colored("                                                      WARNING: QUOTA BELOW 30%",red))
		print("Kapazität benutzt : ["+colored(str(ram[4]),red)+"] GB")
		#log.warning("The QUOTA of the RAM is below 30%")
	print("=======================================================================================================================")
	#####################################################################################
	print("")
	if proc[0] <= 100:
		print("Es laufen momentan ["+colored(str(proc[0]),green)+"] Prozesse.")
	elif proc[0] <= 150:
		print("Es laufen momentan ["+colored(str(proc[0]),yellow)+"] Prozesse."+colored("                                                  WARNING: THRESHOLD EXCEEDED",yellow))
	elif proc[0] > 150:
		print("Es laufen momentan ["+colored(str(proc[0]),red)+"] Prozesse."+colored("                                                  WARNING: THRESHOLD EXCEEDED",red))
	print("=======================================================================================================================")
	print("D.h. ein Prozess verbraucht durchschnittlich ["+colored(str(proc[1]),cyan)+"] MB")
	print("-----------------------------------------------------")
	print("Die drei Ressource intensivsten Prozesse sind:")
	print("1. ->",proc[2])
	print("2. ->",proc[3])
	print("3. ->",proc[4])
	print("=======================================================================================================================")
	#####################################################################################
	print("")
	print("Alle Internen Festplatten")
	print("=======================================================================================================================")
	for item in space:
		usd = item[2][1] - item[1][1]
		print("Driveletter: [{0: <2}] | Size: [{1:4.0f}] GB | Free: [{2:6.1f}] GB | Used: [{3:6.1f}] GB".format(item[0][1],item[2][1],item[1][1],usd))
	print("=======================================================================================================================")
	#####################################################################################
	
if __name__ == "__main__":

	os.system("mode 120,60")
	log.info("--------------- AllEye v."+version+versiondate+" Log ---------------")
	iniVar = readCFG('Settings.ini')
	
	while True:
	
		try:
			ram   = getRAM()
			proc  = getProc()
			space = getSpace()
			visualize(ram,proc,space)
			#time.sleep(1)
		except Exception as e:
			log.error("Error Message:",e)
			continue