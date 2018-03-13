from common_functions import *
from pprint import pprint
from getpass import getpass
from multiprocessing import Pool
import multiprocessing
from itertools import repeat
from cdp_work import *
from datetime import date, datetime
import sqlite3

def enter_info_into_db(done_device,cur,conn):
	today = date.today()
	cur.execute("INSERT INTO devices (site_name,show_run,ip_int_brief,BGP_nei,OSFP_nei,EIGRP_nei,CDP_nei,int_status,updated) VALUES(?,?,?,?,?,?,?,?,?)",
		(done_device['site_name'],
		done_device['run'],
		done_device['int_brief'],
		done_device['bgp'],
		done_device['ospf'],
		done_device['eigrp'],
		done_device['cdp'],
		done_device['int_status'],
		today
		))
	conn.commit()


def main_work(ip, username, password,commands_to_run):
	
	print (ip)
	device_info = {}
	device_info['ip'] = ip
	device_info['new_ips'] = []
	device_info['done_ips'] = []

	try:
		net_connect = make_connection (ip,username,password)
		if net_connect == None:
		
			device_info['can_not_connect'] = ip
			return device_info
		device_info['site_name'] = find_hostname(net_connect)
		for command in commands_to_run:
			device_info[command[1]] = send_command(net_connect,command[0])
			if "Invalid command at" in device_info[command[1]]:
				device_info[command[1]] = send_command(net_connect, command[2])
		for cdp_info in cdpNeighbors(device_info['cdp']):
			if "SEP" not in cdp_info['deviceId']:
				if "AIR" not in cdp_info['platform']:
					device_info['new_ips'].append(cdp_info['ipAddress'])
		device_info['done_ips'] = get_ip (device_info['int_brief'])
	except:
		return None
	return device_info

fail_count = 0
if __name__ == "__main__":

	base_ips_file = "IPs.txt"
	database = 'Network_info.db'
	ips_base = pull_ip_list (base_ips_file)
	ips_done = []
	ips_could_not_connect = []
	ips_to_do = ips_base
	
	conn = sqlite3.connect(database)
	cur = conn.cursor()
	
	
	commands_to_run = [
	['show ip int brief', 'int_brief',""],
	['show run', 'run',""],
	['show ip bgp summary','bgp',""],
	['show ip ospf neighbor','ospf',""],
	['show ip eigrp neighbors','eigrp',""],
	['show cdp entry *', 'cdp','sh cdp entry all'],
	['show interface status','int_status',""],
	['show interface','show_int',""],
	]

	username = input("Username: ")
	password = getpass()
	while len(ips_to_do) != 0:
		pprint (len(ips_to_do))
		with multiprocessing.Pool(processes=75) as pool:
			results = pool.starmap(main_work,zip(ips_to_do, repeat(username), repeat(password),repeat(commands_to_run)))
		ips_to_do =[]
		for done_device in results:
			#print (done_device)
			if done_device == None:
				continue

			try:
				for done_ip_import in done_device['done_ips']:
					ips_done.append(done_ip_import)
				for need_to_do in done_device['new_ips']:
					if need_to_do not in ips_done:
						if need_to_do not in ips_to_do:
							ips_to_do.append(need_to_do)
					else:
						#print ("already there")
						pass
				try:
			#	print ("test")
					enter_info_into_db(done_device,cur,conn)
				except:
				#s
					print ("fail")
			#	fail_count = fail_count+1
				#	enter_info_into_db(done_device,cur,conn)
			except:
				fail_count = fail_count+1
				print ("Fail count: ",fail_count)
				issue = done_device['ip']+ ", Issue with Database\n"
				to_doc_a("Issues.csv", issue)

			

		