import os
import re
import socket
import sys
import time
import datetime
import sqlite3
from common_functions import *



conn = sqlite3.connect('Network_info.db')
cur = conn.cursor()

count_dev_table = 0
count_ip_table = 0

cur.execute("""
			CREATE TABLE devices(
				site_name  TEXT UNIQUE,
				show_run  TEXT,
				ip_int_brief  TEXT,
				BGP_nei TEXT,
				OSFP_nei TEXT,
				EIGRP_nei TEXT,
				CDP_nei TEXT,
				int_status TEXT,
				updated DATE,
				update_attempted DATE
				)""")
conn.commit()
cur.close
conn.close
	