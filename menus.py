import gvmscript
import xml.etree.ElementTree as ET
from auxlib import *

main_actions = ("Create Targets","Create Tasks","Modify Tasks", "Get Latest Reports","Start Scans")
div = "================================================================"

def show_data(options, parsed_data, opt_name): # Show data and return the ID of the selected option
	print(color_default+div)
	print(color_default+opt_name+":\n") 
	dft_ind = opt_name.lower().replace(" ","_") # Index of deafult config in the.ini file
	default = config["default"][dft_ind]
	pos = 0

	if not parsed_data:
		print(color_warning+"No options found por parameter "+opt_name+". It will be left blank.")
		return None

	# Special cases
	if opt_name == "Schedule" and options["main_action"] == "Create Tasks": 
		parsed_data.append({"name": "No Schedule", "id": None})
	if opt_name == "Alerts" and options["main_action"] == "Create Tasks":
		parsed_data.append({"name": "No Alerts", "id": None})

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
	options["modify"] = None # Deafult

	if options["main_action"] == "Create Targets":
		parsed_output = gvmscript.parse_data("<get_port_lists/>", "port_list")
		options["port_list"] = show_data(options, parsed_output, "Port list")

	elif options["main_action"] == "Create Tasks":
		parsed_output = gvmscript.parse_data("<get_configs/>", "config")
		options["scan_config"] = show_data(options, parsed_output, "Scan config")

		parsed_output = gvmscript.parse_data("<get_alerts/>", "alerts")
		options["alerts"] = show_data(options, parsed_output, "Alerts")

		parsed_output = gvmscript.parse_data("<get_schedules/>", "schedule")
		options["schedule"] = show_data(options, parsed_output, "Schedule")

		parsed_output = gvmscript.parse_data("<get_scanners/>", "scanner")
		options["scanner"] = show_data(options, parsed_output, "Scanner")

		order = ["Sequential","Random","Reverse"]
		options["order"] = show_list(order, "Scan order")
	
	elif options["main_action"] == "Modify Tasks":
		modify = ["Scan Config", "Alerts", "Schedule", "Scanner", "Scan Order", "Maximum concurrently executed NVTs per host", "Maximum concurrently scanned hosts"]
		options["modify"] = show_list(modify, "Modify Task Parameter")

		if options["modify"] == "Scan Config":
			parsed_output = gvmscript.parse_data("<get_configs/>", "config")
			options["scan_config"] = show_data(options, parsed_output, "Scan config")

		elif options["modify"] == "Alerts":
			parsed_output = gvmscript.parse_data("<get_alerts/>", "alerts")
			options["alerts"] = show_data(options, parsed_output, "Alerts")

		elif options["modify"] == "Schedule":
			parsed_output = gvmscript.parse_data("<get_schedules/>", "schedule")
			options["schedule"] = show_data(options, parsed_output, "Schedule")

		elif options["modify"] == "Scanner":
			parsed_output = gvmscript.parse_data("<get_scanners/>", "scanner")
			options["scanner"] = show_data(options, parsed_output, "Scanner")

		elif options["modify"] == "Scan Order":
			order = ["Sequential","Random","Reverse"]
			options["order"] = show_list(order, "Scan order")

	logger.info(str(options))


	return options