import subprocess, datetime
from auxlib import *

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

def create_target(host, options):
   ns_result = nslookup(host)

   if ns_result == None and config["settings"]["ignore_ping"]:
      print_log("error", "Unable to ping host "+host+". Skipping...")
      return None

   if "name" in ns_result:
      hostname = ns_result.split("name = ")[1].split("\n")[0][:-1]
   else:
      hostname = host

   if config["settings"]["custom_target_sufix"] == "True":
      

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
      print_log("info", "Target for host "+host+" already exists. Skipping...")
      return None
   else:
      print_log("error", "Unable to create target for host "+host)
      return None

def create_task(host, options):
   pass

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