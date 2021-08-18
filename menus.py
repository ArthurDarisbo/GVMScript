import gvmscript
import xml.etree.ElementTree as ET
from auxlib import *

main_actions = ("Create Targets","Create Tasks","Modify Tasks", "Get Latest Reports","Start Scans")
div = "================================================================"

def show_data(parsed_data, opt_name): # Show data and return the ID of the selected option
	print(color_default+div)
	print(color_default+opt_name+":\n") 
	dft_ind = opt_name.lower().replace(" ","_") # Index of deafult config in the.ini file
	default = config["default"][dft_ind]
	pos = 0

	if not parsed_data:
		print(color_warning+"No options found por parameter "+opt_name+". It will be left blank.")
		return None

	if opt_name == "Schedule": # Special cases with extra options
		parsed_data.append({"name": "No Schedule", "id": None})
	elif opt_name == "Scanner":
		parsed_data.append({"name": "Balanced", "id": None})

	for item in parsed_data:
		print(str(pos)+" - "+item["name"])
		if item != parsed_data[-1]:
			pos += 1

	# Get selection
	while True:
		sel = input(color_default+"\nSelect one of the above options ["+str(default)+"]: ")
		if sel == "": # Blank input so default is used
			sel = default
		try:
			int(sel)
		except:
			print(color_error+"\nInvalid character. Only natural numbers are accepted.")
			continue
		if(int(sel) >= 0 and int(sel) <= pos): # Valid input
			return(parsed_data[int(sel)]["id"]) # Returns the ID of the chosen options
		else: # Invalid input
			print(color_error+"\nSelect a number between 1 and "+str(pos))

def show_list(opt_list, opt_name): # Shows a simple list on screen and gets the selected option
	print(color_default+div)
	print(color_default+opt_name+":\n") 
	dft_ind = opt_name.lower().replace(" ","_") # Index of deafult config in the.ini file
	default = config["default"][dft_ind]
	pos = 0
	for opt in opt_list:
		print(str(pos)+" - "+opt)
		if opt != opt_list[-1]:
			pos += 1
	# Get selection
	while True:
		sel = input(color_default+"\nSelect one of the above options ["+default+"]: ")
		if sel == "":
			sel = default
		try:
			int(sel)
		except:
			print(color_error+"\nInvalid character. Only natural numbers are accepted.")
			continue
		if(int(sel) >= 0 and int(sel) < len(opt_list)): # Valid input
			return(opt_list[int(sel)])
		else: # Invalid input
			print(color_error+"\nSelect a number between 0 and "+str(pos))

def main():
	options = {}
	options["main_action"] = show_list(main_actions, "Main action")

	if "Create Targets" in options["main_action"]:
		parsed_output = gvmscript.parse_data("<get_port_lists/>", "port_list")
		options["port_list"] = show_data(parsed_output, "Port list")

	if "Tasks" in options["main_action"]:
		parsed_output = gvmscript.parse_data("<get_configs/>", "config")
		options["scan_config"] = show_data(parsed_output, "Scan config")

		parsed_output = gvmscript.parse_data("<get_alerts/>", "alerts")
		options["alerts"] = show_data(parsed_output, "Alerts")

		parsed_output = gvmscript.parse_data("<get_schedules/>", "schedule")
		options["schedule"] = show_data(parsed_output, "Schedule")

		parsed_output = gvmscript.parse_data("<get_scanners/>", "scanner")
		options["scanner"] = show_data(parsed_output, "Scanner")

		order = ["Sequential","Random","Reverse"]
		options["order"] = show_list(order, "Scan order")

		logger.info(str(options))

	return options