# checker.py

import alarm
import os
import sys
import time
import subprocess
#import log

def currT():
	t = time.strftime("%H:%M:%S")
	return t
	
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
	proc_avrg = round(ram_used / proc_num,2)
	
	##### Sortiere nach Verbrauch
	rsc_1 = sorted(proc_clean,key=lambda x: x[1], reverse=True)[0]
	rsc_1 = "{0: <14} verbraucht: ~ [{1:4.0f}] MB".format(rsc_1[0],rsc_1[1])
	rsc_2 = sorted(proc_clean,key=lambda x: x[1], reverse=True)[1]
	rsc_2 = "{0: <14} verbraucht: ~ [{1:4.0f}] MB".format(rsc_2[0],rsc_2[1])
	rsc_3 = sorted(proc_clean,key=lambda x: x[1], reverse=True)[2]
	rsc_3 = "{0: <14} verbraucht: ~ [{1:4.0f}] MB".format(rsc_3[0],rsc_3[1])
	
	##### Formatiere Output
	print("")
	print("Es laufen momentan ["+str(proc_num)+"] Prozesse.")
	print("===========================================================")
	print("D.h. ein Prozess verbraucht durchschnittlich ["+str(proc_avrg)+"] GB.")
	print("-----------------------------------------------------------")
	print("Die drei Ressource intensivsten Prozesse sind:")
	print("1. ->",rsc_1)
	print("2. ->",rsc_2)
	print("3. ->",rsc_3)
	print("===========================================================")

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
	ram_avail = round(ram_avail / 1000000000,2)
	ram_free = round(ram_info_free / 1000000,2)
	global ram_used
	ram_used = round(ram_avail - ram_free,2)
	ram_per_r = round(ram_avail / riegel,2)
	print("Im Computer sind ["+str(riegel)+"] Ram-Riegel eingebaut!")
	print("===========================================================")
	print("Gesamtkapazität   : ["+str(ram_avail)+"] GB")
	print("Ram pro Riegel    : ["+str(ram_per_r)+"] GB")
	print("-----------------------------------------------------------")
	print("Kapazität frei    : ["+str(ram_free)+"] GB")
	print("Kapazität benutzt : ["+str(ram_used)+"] GB")
	print("===========================================================")
	
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
				item[1][1] = round(item[1][1])
				#--
				item[2][1] = int(item[2][1])
				item[2][1] = item[2][1] / 1000000000
				item[2][1] = round(item[2][1])
				
				if item[2][1] < item[1][1]:
					del item
					continue
				else:
					pass
			except Exception as e:
				print(e)
				
		tfix.append(item)
		
	del temp
	
	##### Formatiere Output
	print("")
	print("Alle Internen Festplatten")
	print("===========================================================")
	for item in tfix:
		print("| Driveletter: [{0: <2}] | Size: [{1:5.0f}] GB | Free: [{2:5.0f}] GB |".format(item[0][1],item[2][1],item[1][1]))
	print("===========================================================")
	

while True:
	os.system("CLS")
	date = time.strftime("%d.%m.%Y")
	print("------------------")
	print("Date:",date,"|")
	print("Time:",currT(),"  |")
	print("------------------")
	print("")
	getRAM()
	getProc()
	getSpace()
	time.sleep(10)
	
#os.system("PAUSE>NUL")