import subprocess, datetime
from gvm.connections import UnixSocketConnection
from gvm.protocols.gmp import Gmp
from gvm.transforms import EtreeTransform
from gvm.xml import pretty_print
from auxlib import *

path = "/var/run/gvm/gvmd.sock" # sudo chmod -R o+rw /var/run/gvm/
connection = UnixSocketConnection(path=path)
transform = EtreeTransform()

def authenticate(): # Authentication test
   with Gmp(connection, transform=transform) as gmp:
      gmp.authenticate(config["login"]["user"],config["login"]["password"])      
      return(gmp.is_authenticated)

def run_cmd(cmd): # Build an XML object, sends it to GVM CLI and captures the response
   try:
      cmd_input = "gvm-cli --gmp-username "+config["login"]["user"]+" --gmp-password "+config["login"]["password"]+" socket --xml \"<"+cmd+"/>\""
      cmd_output = subprocess.check_output(cmd_input, shell=True).decode("utf-8")
      logging.info("XML Command input: "+cmd_input)
      logging.info("XML Command output: "+cmd_output)
      return cmd_output
   except Exception as e:
      print_log("exception","Failed to run command: " + cmd)

def main():
   with Gmp(connection, transform=transform) as gmp:
      # Retrieve GMP version supported by the remote daemon
      version = gmp.get_version()

      # Prints the XML in beautiful form
      pretty_print(version)

      # Login
      #gmp.authenticate('admin', 'admin')

      # Retrieve all tasks
      tasks = gmp.get_tasks()

      # Get names of tasks
      task_names = tasks.xpath('task/name/text()')
      pretty_print(task_names)