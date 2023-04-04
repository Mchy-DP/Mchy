# Guarantee correct directory is on the path
import sys
from os import path as os_path
sys.path.append(os_path.dirname(os_path.dirname(__file__)))

# Call the command line program entry point
from mchy.cmdln.main import main_by_cmdln  # noqa  #  pycodestyle doesn't like imports after ANY code even when sensible
main_by_cmdln()
