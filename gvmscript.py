import subprocess, os, base64
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
	root = ET.fromstring(cmd_output)
	parsed_data = []
	try:
		for x in root.findall(data_type):
			id = x.attrib["id"]
			name = x.find("name").text
			parsed_data.append({"name": name, "id": id})
		logger.info("Parsed data: "+str(parsed_data))
	except KeyError:
		return None
	return parsed_data

def get_target(host, targets): # Searches for a host's target
   root = ET.fromstring(targets)
   try:
      for x in root.findall("target"):
         id = x.attrib["id"]
         hosts = x.find("hosts").text
         if hosts == host:
            return id
   except KeyError:
      print_log("error", "Host "+host+" has no targets. Create a target first")
      return None

def get_tasks(target_id): # Get all tasks for host
   parsed_tasks = []
   cmd_output = run_cmd("<get_targets target_id='"+target_id+"' tasks='1'/>")
   if "OK" in cmd_output and "task id" in cmd_output:
      tasks = cmd_output.split("<tasks>")[1].split("</tasks>")[0].split("</task>")
      for task in tasks:
         if task == "":
            continue
         id = task.split("<task id=\"")[1].split("\"")[0]
         name = task.split("<name>")[1].split("</name>")[0]
         parsed_tasks.append({"name": name, "id": id})
      logger.info("Parsed tasks: "+str(parsed_tasks))
   else:
      return None
   return parsed_tasks

def build_target(host, options): # Builds an XML object to create a target
   xml = "<create_target>"
   xml += "<name>"+options["hostname"]+"</name>"
   xml += "<hosts>"+host+"</hosts>"
   xml += "<port_list id='"+options["port_list"]+"'></port_list>"
   if(config["settings"]["use_comments"] == "True"):
      xml += "<comment>"+config["settings"]["comment"]+"</comment>"
   xml += "<reverse_lookup_only>"+config["parameters"]["reverse_lookup_only"]+"</reverse_lookup_only>"
   xml += "<reverse_lookup_unify>"+config["parameters"]["reverse_lookup_unify"]+"</reverse_lookup_unify>"
   xml += "</create_target>"
   return xml

def build_task(host, options, task_id = "None"): # Builds an XML object to create or modify a task and evaluates the output
   if options["main_action"] == "Create Tasks":
      xml = "<create_task>"
      xml += "<target id='"+options["target_id"]+"'/>"         
      xml += "<name>"+options["hostname"]+"</name>"

   else:
      xml = "<modify_task task_id='"+task_id+"'>"

   if options["main_action"] == "Create Tasks" or options["modify"] == "Scan Config":
      xml += "<config id='"+options["scan_config"]+"'/>"

   if options["main_action"] == "Create Tasks" or options["modify"] == "Alerts":
      if options["alerts"] != None:
         xml += "<alert id='"+options["alerts"]+"'/>"

   if options["main_action"] == "Create Tasks" or options["modify"] == "Schedule":
      if options["schedule"] != None:
         xml += "<schedule id='"+options["schedule"]+"'/>"  

   if options["main_action"] == "Create Tasks" or options["modify"] == "Scanner":
      xml += "<scanner id='"+options["scanner"]+"'/>"

   if options["main_action"] == "Create Tasks" or options["modify"] == "Scan Order":
      xml += "<hosts_ordering>"+options["order"]+"</hosts_ordering>"

   if options["main_action"] == "Create Tasks":
      if(config["settings"]["use_comments"] == "True"):
         xml += "<comment>"+config["settings"]["comment"]+"</comment>"

      xml += "<alterable>"+config["parameters"]["alterable_task"]+"</alterable>"
   
   if options["main_action"] == "Create Tasks" or "Maximum" in options["modify"]:
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

   if options["main_action"] == "Create Tasks" or options["modify"] == "Maximum concurrently executed NVTs per host":
      xml += "<preference>"
      xml += "<scanner_name>max_checks</scanner_name>"
      xml += "<value>"+config["parameters"]["max_nvt"]+"</value>"
      xml += "</preference>" 

   if options["main_action"] == "Create Tasks" or options["modify"] == "Maximum concurrently scanned hosts":
      xml += "<preference>"
      xml += "<scanner_name>max_hosts</scanner_name>"
      xml += "<value>"+config["parameters"]["max_scanned"]+"</value>"
      xml += "</preference>"

   if options["main_action"] == "Create Tasks" or "Maximum" in options["modify"]:
      xml += "</preferences>"

   if options["main_action"] == "Create Tasks":
      xml += "</create_task>"
   else:
      xml += "</modify_task>"

   cmd_output = run_cmd(xml)

   if "status=\"201\"" in cmd_output:
      print_log("success", "Successfully created a task for host "+host)
      id = cmd_output.split("id=\"")[1].split("\"")[0]
      return id
   elif "status=\"200\"" in cmd_output:
      print_log("success", "Successfully modified a task for host "+host)
   elif "Config and Scanner types mismatch" in cmd_output:
      print_log("error", "Config and Scanner types mismatch in a task of host "+host)
   else:
      print_log("error", "Unable to create or modify a task for host "+host)

def create_target(host, targets, options): # Creates a target
   ns_result = nslookup(host)

   if ns_result == None and config["settings"]["ignore_ping"] == "False": # Ping failed and necessary
      print_log("error", "Unable to ping host "+host+". Skipping...")
      return None

   if host in targets:
      print_log("warning", "A target with host "+host+" already exists")

   if "name" in ns_result:
      options["hostname"] = ns_result.split("name = ")[1].split("\n")[0][:-1]
   else:
      options["hostname"] = host

   if config["settings"]["custom_target_sufix"] == "True":
      options["hostname"] += " - " + config["settings"]["target_sufix"]

   xml = build_target(host, options)
   cmd_output = run_cmd(xml)

   if "status=\"201\"" in cmd_output:
      print_log("success", "Successfully created a target for host "+host)
      id = cmd_output.split("id=\"")[1].split("\"")[0]
      return id
   elif "Target exists already" in cmd_output:
      print_log("error", "Same exact target for host "+host+" already exists. Skipping...")
      return None
   else:
      print_log("error", "Unable to create target for host "+host)
      return None

def create_task(host, targets, options): # Creates or modifies a task
   ns_result = nslookup(host)

   if ns_result == None and config["settings"]["ignore_ping"] == "False": # Ping failed and necessary
      print_log("error", "Unable to ping host "+host+". Skipping...")
      return 

   if "name" in ns_result: # NS Lookup successful 
      options["hostname"] = ns_result.split("name = ")[1].split("\n")[0][:-1]
   else:
      options["hostname"] = host

   if host not in targets: # No target found for host
      print_log("error", "Host "+host+" has no targets. Unable to create or modify a task")
      return 

   if config["settings"]["custom_task_sufix"] == "True": # Add sufix
      options["hostname"] += " - " + config["settings"]["task_sufix"]

   options["target_id"] = get_target(host, targets) # Get target ID
   if options["target_id"] == None: # Propagate error
      return

   if options["main_action"] == "Create Tasks": # Create new task
      build_task(host, options)
   else: # Modify all tasks
      task_list = get_tasks(options["target_id"])

      if task_list == None:
         print_log("error", "No tasks found for host "+host)

      for task in task_list:
         build_task(host, options, task["id"])

def get_reports(host, targets, options):
   options["target_id"] = get_target(host, targets)

   if options["target_id"] == None: # Propagate error
      print_log("error", "Host "+host+" has no target")
      return

   task_list = get_tasks(options["target_id"])

   if task_list == None:
      print_log("error", "No tasks found for host "+host)

   for task in task_list:
      task_data = run_cmd("<get_tasks task_id='"+task["id"]+"' details='1'/>")
      if "report id" in task_data:
         report_id = task_data.split("<last_report><report id=\"")[1].split("\"")[0]
         cmd_output = run_cmd("<get_reports report_id='"+report_id+"' format_id='"+config["reports"]["report_format"]+"'/>")
         extension = cmd_output.split("extension=\"")[1].split("\"")[0]
         report = cmd_output.split("</report_format>")[1].split("</report>")[0]
         filename = config["reports"]["report_folder"] + "/" + host + "_" + task["name"] + "." + extension

         if not os.path.exists(config["reports"]["report_folder"]):
            os.makedirs(config["reports"]["report_folder"])

         with open(filename, "wb") as file:
            if extension == "pdf": # Convert from base64
               file.write(base64.b64decode(report))
            else:
               file.write(report)

         print_log("success", "Exported latest report from task "+task["name"]+" of host "+host)

      else:
         print_log("warning", "Host "+host+" has no reports")

def start_tasks(host, targets, options):
   options["target_id"] = get_target(host, targets)

   if options["target_id"] == None: # Propagate error
      print_log("error", "Host "+host+" has no target")
      return

   task_list = get_tasks(options["target_id"])

   if task_list == None:
      print_log("error", "No tasks found for host "+host)

   for task in task_list:
      cmd_output = run_cmd("<start_task task_id='"+task["id"]+"'/>")

   if "status=\"202\"" in cmd_output:
      print_log("success", "Started task "+task["name"]+" of host "+host)
   else:
      print_log("error", "Unable to start task "+task["name"]+" of host "+host)