import configparser, logging, sys
from datetime import datetime

# Terminal color codes
color_default = "\033[1;37m"
color_error = "\033[31m"
color_warning = "\033[93m"
color_info = "\033[96m"
color_ok = "\033[92m"

# Initialize logger
logger = logging.getLogger()
date_fmt = "%d/%m/%Y - %I:%M:%S %p"
msg_fmt = "%(asctime)s - %(message)s - %(levelname)-s"
logging.basicConfig(level=logging.INFO, filename="log.log", format=msg_fmt, datefmt=date_fmt)

# Prints and logs messages
def print_log(category, message):
	date_fmt = datetime.now().strftime("%H:%M:%S")
	msg_fmt = date_fmt + " " + category.upper() + ": " + message
	if(category == "exception"):
		print(color_error + msg_fmt)
		logger.exception(message)
	elif(category == "error"):
		print(color_error + msg_fmt)
		logger.error(message)
	elif(category == "warning"):
		print(color_warning + msg_fmt)
		logger.warning(message)
	elif(category == "info"):
		print(color_info + msg_fmt)
		logger.info(message)
	elif(category == "success"):
		print(color_ok + msg_fmt)
		logger.info(message)

# Initialize configuration file
try:
	config = configparser.ConfigParser(comment_prefixes=(';'), inline_comment_prefixes=('#'))
	config.read("./config.ini")
except Exception as e:
	print_log("exception","Failed to find or read config file.")
	sys.exit()