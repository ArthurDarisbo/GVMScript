import subprocess
from auxlib import *
import xml.etree.ElementTree as ET

def run_cmd(xml): # Build a command with a XML object, sends it to GVM CLI and captures the response
   try:
      cmd_input = ["gvm-cli", "--gmp-username", config["login"]["user"], "--gmp-password", config["login"]["password"], "socket", "--xml", xml]
      cmd_output = subprocess.run(cmd_input, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout.decode("utf-8")
      logging.info("XML Command input: "+str(cmd_input))
      logging.info("XML Command output: "+cmd_output)
      return cmd_output
   except subprocess.CalledProcessError:
      logger.exception("Failed to run command: " + xml)
      return None

def nslookup(host): # Pings target and captures the response
   try:
      cmd_input = "nslookup "+host
      cmd_output = subprocess.check_output(cmd_input, shell=True).decode("utf-8")
      if "server can't find" in cmd_output:
         raise Exception
   except:
      cmd_output = None
   logging.info("Nslookup Command output: "+str(cmd_output))
   return cmd_output

def authenticate(): # Authentication test
   cmd_output = run_cmd("<get_tasks/>")
   if "Error 400" in cmd_output:
      return False
   else:
      return True

def parse_data(xml, data_type): # Gets and parses the output from CLI to a list
	cmd_output = run_cmd(xml)
	root = ET.fromstring(cmd_output).findall(data_type)
	parsed_data = []
	try:
		for x in root:
			id = x.attrib["id"]
			name = x.find("name").text
			parsed_data.append({"name": name, "id": id})
	except KeyError:
		return None
	return parsed_data

def find_target(host, targets): # Searches for host's target
   root = ET.fromstring(targets).findall("target")
   try:
      for x in root:
         id = x.attrib["id"]
         hosts = x.find("hosts").text
         if hosts == host:
            return id
   except KeyError:
      print_log("error", "Host "+host+" has no targets. Create a target first")
      return None

def build_target(host, hostname, options): # Creates an XML object to create a target
   xml = "<create_target>"
   xml += "<name>"+hostname+"</name>"
   xml += "<hosts>"+host+"</hosts>"
   xml += "<port_list id='"+options["port_list"]+"'></port_list>"
   if(config["settings"]["use_comments"] == "True"):
      xml += "<comment>"+config["settings"]["comment"]+"</comment>"
   xml += "<reverse_lookup_only>"+config["parameters"]["reverse_lookup_only"]+"</reverse_lookup_only>"
   xml += "<reverse_lookup_unify>"+config["parameters"]["reverse_lookup_unify"]+"</reverse_lookup_unify>"
   xml += "</create_target>"
   return xml

def build_task(hostname, options, task_id = "None"): # Creates an XML object to create or modify a task
   if options["main_action"] == "Create Tasks":
      xml = "<create_task>"
      xml += "<target id='"+options["target_id"]+"'/>"   
      if options["alerts"] != None:
         xml += "<alert id='"+options["alerts"]+"'/>"  
   else:
      xml = "<modify_task task_id='"+task_id+"'></modify_task>"

   xml += "<name>"+hostname+"</name>"
   xml += "<config id='"+options["scan_config"]+"'/>"
   xml += "<scanner id='"+options["scanner"]+"'/>"

   if(config["settings"]["use_comments"] == "True"):
      xml += "<comment>"+config["settings"]["comment"]+"</comment>"
   if options["schedule"] != None:
      xml += "<schedule id='"+options["schedule"]+"'/>"  
   
   if options["main_action"] == "Create Tasks":
      xml += "<alterable>"+config["parameters"]["alterable_task"]+"</alterable>"
      xml += "<hosts_ordering>"+options["order"]+"</hosts_ordering>"
   xml += "<preferences>"

   if options["main_action"] == "Create Tasks":
      xml += "<preference>"
      xml += "<scanner_name>assets_apply_overrides</scanner_name>"
      xml += "<value>"+config["parameters"]["overrides"]+"</value>"
      xml += "</preference>"
   
   xml += "<preference>"
   xml += "<scanner_name>in_assets</scanner_name>"
   xml += "<value>"+config["parameters"]["result_assets"]+"</value>"
   xml += "</preference>"
   xml += "<preference>"
   xml += "<scanner_name>auto_delete</scanner_name>"
   xml += "<value>"+config["parameters"]["auto_delete"]+"</value>"
   xml += "</preference>"
   xml += "<preference>"
   xml += "<scanner_name>auto_delete_data</scanner_name>"
   xml += "<value>"+config["parameters"]["delete_over"]+"</value>"
   xml += "</preference>"
   xml += "<preference>"
   xml += "<scanner_name>max_checks</scanner_name>"
   xml += "<value>"+config["parameters"]["max_nvt"]+"</value>"
   xml += "</preference>" 
   xml += "<preference>"
   xml += "<scanner_name>max_hosts</scanner_name>"
   xml += "<value>"+config["parameters"]["max_scanned"]+"</value>"
   xml += "</preference>"
   xml += "</preferences>"

   if options["main_action"] == "Create Tasks":
      xml += "</create_task>"
   else:
      xml += "</modify_task>"

   return xml

def operate_task(host, hostname, options):
   xml = build_task(hostname, options)
   cmd_output = run_cmd(xml)

   if "status=\"201\"" in cmd_output:
      if options["main_action"]:
         print_log("success", "Successfully created a task for host "+host)
      else:
         print_log("success", "Successfully modified a task for host "+host)
      id = cmd_output.split("id=\"")[1].split("\"")[0]
      return id
   else:
      print_log("error", "Unable to create or modify a task for host "+host)
      return None

def create_target(host, targets, options):
   ns_result = nslookup(host)

   if ns_result == None and config["settings"]["ignore_ping"] == "False": # Ping failed and necessary
      print_log("error", "Unable to ping host "+host+". Skipping...")
      return None

   if host in targets:
      print_log("warning", "A target with host "+host+" already exists")

   if "name" in ns_result:
      hostname = ns_result.split("name = ")[1].split("\n")[0][:-1]
   else:
      hostname = host

   if config["settings"]["custom_target_sufix"] == "True":
      hostname += " - " + config["settings"]["target_sufix"]

   xml = build_target(host, hostname, options)
   cmd_output = run_cmd(xml)

   if "status=\"201\"" in cmd_output:
      print_log("success", "Successfully created a target for host "+host)
      id = cmd_output.split("id=\"")[1].split("\"")[0]
      #return id
   elif "Target exists already" in cmd_output:
      print_log("warning", "Same exact target for host "+host+" already exists. Skipping...")
      #return None
   else:
      print_log("error", "Unable to create target for host "+host)
      #return None

def create_task(host, targets, options, tasks = "None"): # Create or modify a task
   ns_result = nslookup(host)

   if ns_result == None and config["settings"]["ignore_ping"] == "False": # Ping failed and necessary
      print_log("error", "Unable to ping host "+host+". Skipping...")
      return None

   if "name" in ns_result: # NS Lookup successful 
      hostname = ns_result.split("name = ")[1].split("\n")[0][:-1]
   else:
      hostname = host

   if host not in targets: # No target found for host
      print_log("error", "Host "+host+" has no targets. Unable to create or modify a task")
      return None

   if config["settings"]["custom_task_sufix"] == "True": # Add sufix
      hostname += " - " + config["settings"]["task_sufix"]

   options["target_id"] = find_target(host, targets) # Get target ID
   if options["target_id"] == None: # Propagate error
      return None

   if options["main_action"] == "Create Tasks": # Create new task
      cmd_output = operate_task(host, hostname, options)
   else: # Modify all tasks
      task_list = parse_data(tasks, "task") # Gets all tasks
      for task in task_list:
         cmd_output = operate_task(host, hostname, options)