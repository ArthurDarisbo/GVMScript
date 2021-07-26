import gvmscript, sys
import xml.etree.ElementTree as ET
from auxlib import *

main_actions = ("Create Targets and Tasks","Update Tasks","Get Latest Reports","Perform a Sanity Check")
sub_menu = ("Create Targets", "Create Tasks","Create Targets and Tasks","Create Targets and Create/Update Tasks")
div = "================================================================"

def parse_data(cmd_output, data_type): # Parses the output from CLI to a list
	root = ET.fromstring(cmd_output).findall(data_type)
	parsed_data = []
	for x in root:
		id = x.attrib["id"]
		name = x.find("name").text
		parsed_data.append({"name": name, "id": id})
	return parsed_data

def show_data(parsed_data, opt_name): # Show data and return the ID of the selected option
	pos = 0
	dft_ind = opt_name.lower().replace(" ","_") # Index of deafult config in the.ini file
	default = int(config["default"][dft_ind])
	print(color_default+div)
	print(color_default+opt_name+":\n") 
	for item in parsed_data:
		print(str(pos)+" - "+item["name"])
		if item != parsed_data[-1]:
			pos += 1
	# Special cases
	if opt_name == "Schedule":
		print(color_default+str(pos)+" - No Schedule")
	elif opt_name == "Scanner":
		print(color_default+str(pos)+" - Balanced")
	# Get selection
	while True:
		sel = input(color_default+"\nSelect one of the above options ["+str(default)+"]: ")
		if sel == "": # Blank input so default is returned
			return(parsed_data[default]["id"])
		try:
			int(sel)
		except:
			print(color_error+"\nInvalid character. Only natural numbers are accepted.")
			continue
 		# Special cases check
		if(int(sel) == pos+1): # Max position + 1 has been selected, so checks for special cases
			if opt_name == "Scanner":
				return # TO-DO: SCANNER BALANCING
			elif opt_name == "Schedule":
				return "No Schedule"
			else: # Pos+1 selected but no special case: invalid
				print(color_error+"\nSelect a number between 1 and "+str(pos))
				continue
		elif(int(sel) >= 0 and int(sel) <= pos): # Valid input
			return(parsed_data[int(sel)]["id"]) # Returns the ID of the chosen options
		else:
			if(opt_name == "Scanner" or opt_name == "Schedule"): # Checks for special cases
				print(color_error+"\nSelect a number between 1 and "+str(pos+1)) # Limit is pos + 1
			else:
				print(color_error+"\nSelect a number between 1 and "+str(pos))

def show_list(opt_list, opt_name): # Shows a simple list on screen and gets the selected option
	print(color_default+div)
	print(color_default+opt_name+":\n") 
	pos = 0
	default = 0
	for opt in opt_list:
		print(str(pos)+" - "+opt)
		if opt != opt_list[-1]:
			pos += 1
	# Get selection
	while True:
		sel = input(color_default+"\nSelect one of the above options ["+str(default)+"]: ")
		if sel == "":
			if(opt_name == "Main action" and default == 0):
				return show_list(sub_menu, "Main action submenu")
			else:
				return(opt_list[default])
		try:
			int(sel)
		except:
			print(color_error+"\nInvalid character. Only natural numbers are accepted.")
			continue
		if(int(sel) < 0 or int(sel) >= len(opt_list)):
			print(color_error+"\nSelect a number between 0 and "+str(pos))
		elif(opt_name == "Main action" and sel == "0"):
			return show_list(sub_menu, "Main action submenu")
		else:
			return(opt_list[int(sel)])

def main():
	options = {}
	options["main_action"] = show_list(main_actions, "Main action")

	if "Create Targets" in options["main_action"]:
		parsed_output = parse_data(gvmscript.run_cmd("get_port_lists"), "port_list")
		options["portlist_id"] = show_data(parsed_output, "Port list")
		print(options["portlist_id"])

	if "Tasks" in options["main_action"]:
		parsed_output = parse_data(gvmscript.run_cmd("get_port_lists"), "port_list")
		options["portlist_id"] = show_data(parsed_output, "Port list")
		print(options["portlist_id"])
		
	return options
