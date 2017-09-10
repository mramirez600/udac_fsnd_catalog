#!/usr/bin/python

import sys
import logging

logging.basicConfig(stream=sys.stderr)
sys.path.insert(0,"/var/www/udac_fsnd_catalog")

from init import app as application
application.secret_key = 'super_secret_key'
