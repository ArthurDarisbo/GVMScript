import sys, os, menus, gvmscript
from auxlib import *

# sudo chmod -R o+rw /opt/gvm/var/run/
# gvm-cli --gmp-username gvmadmin --gmp-password StrongPass socket --xml "<get_tasks/>"

# Gets host list
def get_hosts(): 
	path = config["settings"]["hosts_file"]
	if(os.path.exists(path)): # Path exists
		with open(path, "r") as file:
			hosts = file.read().splitlines()
		return hosts
	else:
		print_log("error","Hosts file not found.")
		sys.exit()

if __name__ == "__main__": 
	if not gvmscript.authenticate():
		print_log("error","Autentication failed. Check your credentials.")
		sys.exit()

	hosts = get_hosts()
	options = menus.main()
	targets = gvmscript.run_cmd("<get_targets/>")
	
	for host in hosts:
		if options["main_action"] == "Create Targets":
			gvmscript.create_target(host, targets, options)

		elif options["main_action"] == "Create Tasks":
			gvmscript.create_task(host, targets, options, None)

		elif options["main_action"] == "Modify Tasks":
			tasks = gvmscript.run_cmd("<get_tasks/>")
			gvmscript.create_task(host, targets, options, tasks)

		elif options["main_action"] == "Get Latest Reports":
			pass

		elif options["main_action"] == "Start Scans":
			pass