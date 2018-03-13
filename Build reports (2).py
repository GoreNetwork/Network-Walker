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
	command =""" select site_name,int_status,ip_int_brief  from devices;"""
	output = cur.execute(command)
	return output

db_name = 'Network_info - Copy.db'

count = pull_count(db_name)

for each in count:
	print (each)

all_devices_int_status = pull_int_status(db_name)

#for each in all_devices_int_status:
#	pprint (each)

ports_I_dont_want = ['routed','trunk','SFP','Not Present','unknown']

subnets_file = "subnets.txt"
unwanted_subnets = get_subnets_from_file(subnets_file)

output_doc = "output.csv"

to_doc_w(output_doc,'')

for one_device in all_devices_int_status:
	hostname = one_device[0]
	int_brief = one_device[2]
	one_device_int_status = one_device[1]
	ips = get_ip (int_brief)
	we_want_this = True

	if "adcsa" in hostname:
		print (hostname,one_device_int_status)
	if we_want_this == False:
		continue


	for ip in ips:
		tmp = ip_in_subnet_list(ip,unwanted_subnets)
		if tmp == True:
			we_want_this = False


	#pprint(hostname)

	count = 0

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
#	to_doc_a(output_doc,hostname_count)
	#pprint(hostname_count)




