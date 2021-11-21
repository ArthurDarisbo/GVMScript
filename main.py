import sys, os, menus, gvmscript
from auxlib import *

# sudo chmod -R o+rw /opt/gvm/var/run/

def get_hosts(): # Gets host list
	path = config["settings"]["hosts_file"]
	if(os.path.exists(path)): # Path exists
		with open(path, "r") as file:
			hosts = file.read().splitlines()
		return hosts
	else:
		sys.exit("error","Hosts file not found.")

if __name__ == "__main__": 
	if len(sys.argv) != 3:
		print_log("error", "Please insert only your username and password as parameters. Example: main.py username password")
		sys.exit()

	if not gvmscript.authenticate():
		print_log("error","Autentication failed. Check your credentials.")
		sys.exit()

	hosts = get_hosts()
	options = menus.main()
	targets = gvmscript.run_cmd("<get_targets/>")
	
	for host in hosts:
		if options["main_action"] == "Create Targets":
			gvmscript.create_target(host, targets, options)

		elif options["main_action"] == "Create Tasks" or options["main_action"] == "Modify Tasks":
			gvmscript.create_task(host, targets, options)

		elif options["main_action"] == "Get Latest Reports":
			gvmscript.get_reports(host, targets, options)

		elif options["main_action"] == "Start Tasks":
			gvmscript.start_tasks(host, targets, options)