import sys, os, menus, gvmscript
from auxlib import *

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
	if not gvmscript.authenticate(): # Authentication test failed
		print_log("error","Autentication failed. Check user and password.")
		sys.exit()
	
	hosts = get_hosts()
	options = menus.main()
	#print(gvmscript.run_cmd("<get_port_lists/>"))



