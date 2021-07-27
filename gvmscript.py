import subprocess, datetime
from auxlib import *

# sudo chmod -R o+rw /opt/gvm/var/run/

def run_cmd(cmd): # Build an XML object, sends it to GVM CLI and captures the response
   try:
      cmd_input = "gvm-cli --gmp-username "+config["login"]["user"]+" --gmp-password "+config["login"]["password"]+" socket --xml \"<"+cmd+"/>\""
      cmd_output = subprocess.check_output(cmd_input, shell=True).decode("utf-8")
      logging.info("XML Command input: "+cmd_input)
      logging.info("XML Command output: "+cmd_output)
      return cmd_output
   except Exception:
      print_log("exception","Failed to run command: " + cmd)

def authenticate(): # Authentication test
   try:
      cmd_input = "gvm-cli --gmp-username "+config["login"]["user"]+" --gmp-password "+config["login"]["password"]+" socket --xml \"<get_tasks/>\""
      cmd_output = subprocess.check_output(cmd_input, shell=True).decode("utf-8")
      logging.info("XML Command input: "+cmd_input)
      logging.info("XML Command output: "+cmd_output)
      return True
   except:
      return False

def ping(): # Pings target and captures the response
   cmd_