import sqlite3
from pprint import pprint
from common_functions import *

def pull_count(db_name):
	conn = sqlite3.connect(db_name)
	cur = conn.cursor()
	command ="""select count(site_name)  from devices;
	"""
	output = cur.execute(command)
	return output


def pull_int_status(db_name):
	conn = sqlite3.connect(db_name)
	cur = conn.cursor()
	command =""" select site_name,int_status  from devices;"""
	output = cur.execute(command)
	return output

db_name = 'Network_info - Copy (2).db'

count = pull_count(db_name)

for each in count:
	print (each)

all_devices_int_status = pull_int_status(db_name)

#for each in all_devices_int_status:
#	pprint (each)

ports_I_dont_want = ['routed','trunk','disabled','SFP','Not Present','unknown']



output_doc = "output.csv"

to_doc_w(output_doc,'')

for one_device in all_devices_int_status:
	hostname = one_device[0]
	#pprint(hostname)
	count = 0
	one_device_int_status = one_device[1]
	one_device_int_status = one_device_int_status.split("\n")
	for line in one_device_int_status:
		#print (line)
		add_line = False
		if "connect" in line:
			#print (line)
			add_line = True
		for bad_port in ports_I_dont_want:
			if bad_port in line:
				add_line = False
		if add_line == True:
			count = count+1
	hostname_count = hostname + ","+str(count)+"\n"
	to_doc_a(output_doc,hostname_count)
	#pprint(hostname_count)




