# alarm.py

import sys
import time
import ctypes

def refresh():
	global lastexectime
	lastexectime = time.time()
	
def checkcooldown(now,lastexectime):
	dif = now - lastexectime
	if dif > 10:
		cd = "off"
	else:
		cd = "on"
	return cd

def raiseAlarm(cause,lastexectime):
	now = time.time()
	cd = checkcooldown(now,lastexectime)
	if cd == "off":
		ctypes.windll.user32.MessageBoxW(0, cause, "Alarm Popup", 1)
		refresh()
		return
	else:
		return
	
if __name__ == "__main__":
    print("ERROR: This is not the main application")
    print("    -> Please start checker.py to use AllEye in it's appropiate manner.")
    time.sleep(10)
    sys.exit()