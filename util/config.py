import ConfigParser
import getopt
import os
import sys
import logging

def usage():
   print "python app.py [-h|--help] [-i|--ini <settings ini file >]"
   print "If no settings file specified, will look for ecommerce.ini in the current directory."
   if not os.path.isfile("ecommerce.ini"):
        print "\nCould not find the ecommerce.ini file in the current directory\n"

config = ConfigParser.ConfigParser()

def configure(argv):

    global config

    file = "ecommerce.ini"

    try:
        opts, args = getopt.getopt(argv, "hi:", ["help", "ini="])
        for opt, arg in opts:
            if opt in ("-h", "--help"):
                usage()
                sys.exit(0)
            elif opt in ("-i", "--ini"):
                file = arg
    except getopt.GetoptError:
        usage()
        sys.exit(1)

    print "Reading from config file: %s" % (file)

    if os.path.isfile(file):
        config.read(file)
    else:
        usage()
        sys.exit(2)

    #assert (config.has_section('auth'))  == True
    #assert (config.has_section('db'))  == True
    #assert (config.has_section('bottle'))  == True
    #assert (config.has_section('logging'))  == True
    #assert (config.has_option('bottle', 'listen_port'))  == True

    if config.has_option('logging', 'logfile'):
        logfile = config.get('logging', 'logfile')
        logging.basicConfig(filename=logfile, level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')   
    else:
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

