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

def authenticate(): # Authentication test
   cmd_output = run_cmd("<get_tasks/>")
   if "Error 400" in cmd_output:
      return False
   else:
      return True

def create_target(host, targets, options):
   ns_result = nslookup(host)

   if ns_result == None and config["settings"]["ignore_ping"] == "False":
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

   xml = "<create_target>"
   xml += "<name>"+hostname+"</name>"
   xml += "<hosts>"+host+"</hosts>"
   xml += "<port_list id='"+options["port_list"]+"'></port_list>"
   if(config["settings"]["use_comments"] == "True"):
      xml += "<comment>"+config["settings"]["comment"]+"</comment>"
   xml += "<reverse_lookup_only>"+config["parameters"]["reverse_lookup_only"]+"</reverse_lookup_only>"
   xml += "<reverse_lookup_unify>"+config["parameters"]["reverse_lookup_unify"]+"</reverse_lookup_unify>"
   xml += "</create_target>"

   cmd_output = run_cmd(xml)

   if "status=\"201\"" in cmd_output:
      print_log("success", "Successfully created a target for host "+host)
      id = cmd_output.split("id=\"")[1].split("\"")[0]
      return id
   elif "Target exists already" in cmd_output:
      print_log("warning", "Same target for host "+host+" already exists. Skipping...")
      return None
   else:
      print_log("error", "Unable to create target for host "+host)
      return None

def create_task(host, targets, options):
   ns_result = nslookup(host)

   if ns_result == None and config["settings"]["ignore_ping"] == "False":
      print_log("error", "Unable to ping host "+host+". Skipping...")
      return None

   if "name" in ns_result:
      hostname = ns_result.split("name = ")[1].split("\n")[0][:-1]
   else:
      hostname = host

   if host not in targets:
      print_log("error", "Host "+host+" has no targets. Unable to create a task")
      return None

   if config["settings"]["custom_task_sufix"] == "True":
      hostname += " - " + config["settings"]["task_sufix"]

   if "target_id" not in options:
      root = ET.fromstring(targets).findall("target")
      try:
         for x in root:
            id = x.attrib["id"]
            hosts = x.find("hosts").text
            if hosts == host:
               options["target_id"] = id
      except KeyError:
         print_log("error", "Host "+host+" has no targets. Create a target first")
         return None

   xml = "<create_task>"
   xml += "<name>"+hostname+"</name>"
   xml += "<target id='"+options["target_id"]+"'/>"
   xml += "<config id='"+options["scan_config"]+"'/>"
   xml += "<scanner id='"+options["scanner"]+"'/>"

   if(config["settings"]["use_comments"] == "True"):
      xml += "<comment>"+config["settings"]["comment"]+"</comment>"
   if options["alerts"] != None:
      xml += "<alert id='"+options["alerts"]+"'/>"  
   if options["schedule"] != None:
      xml += "<schedule id='"+options["schedule"]+"'/>"  
   
   xml += "<alterable>"+config["parameters"]["alterable_task"]+"</alterable>"
   xml += "<hosts_ordering>"+options["order"]+"</hosts_ordering>"
   xml += "<preferences>"
   xml += "<preference>"
   xml += "<scanner_name>in_assets</scanner_name>"
   xml += "<value>"+config["parameters"]["result_assets"]+"</value>"
   xml += "</preference>"
   xml += "<preference>"
   xml += "<scanner_name>assets_apply_overrides</scanner_name>"
   xml += "<value>"+config["parameters"]["overrides"]+"</value>"
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
   xml += "</create_task>"

   cmd_output = run_cmd(xml)

   if "status=\"201\"" in cmd_output:
      print_log("success", "Successfully created a task for host "+host)
      id = cmd_output.split("id=\"")[1].split("\"")[0]
      return id
   else:
      print_log("error", "Unable to create target for host "+host)
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