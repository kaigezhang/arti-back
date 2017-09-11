# project folder
import os

# DATA_DIR = '/home/ubuntu/code/20170908/yinwen/back/'
# DATA_DIR = os.path.abspath(__file__)

APP_DIR = os.path.abspath(os.path.dirname(__file__))  # This directory
PROJECT_ROOT = os.path.abspath(os.path.join(APP_DIR, os.pardir))

# pdf folder
PDF_DIR = PROJECT_ROOT + '/uploads/pdfs/'
HTML_DIR = PROJECT_ROOT + '/uploads/htmls/'
