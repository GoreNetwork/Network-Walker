import os
import re
import socket
import sys
import netmiko
from getpass import getpass
from ciscoconfparse import CiscoConfParse
from pprint import pprint

def pull_ip_list (file_name):
	file = ""
	for line in open(file_name, 'r').readlines():
		file = file+line
	return get_ip (file)


def get_mac (input):
	return(re.findall(r'(?:[0-9a-fA-F].?){12}', input))

def get_ip (input):
	return(re.findall(r'(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)', input))
	
def read_doc (file_name):
	doc = []
	for line in open(file_name, 'r').readlines():
		doc.append(line)
	return doc

def to_doc_w(file_name, varable):
	f=open(file_name, 'w')
	f.write(varable)
	f.close()	

def to_doc_a(file_name, varable):
	f=open(file_name, 'a')
	f.write(varable)
	f.close()	

def remove_start(line,remove_this):
	line_search = re.search(remove_this,line)
	line = line[line_search.end()+1:]
	return line
	
def make_list_string_with_spaces(list):
	line = str(list)
	line = line.replace("[","")
	line = line.replace("]","")
	line = line.replace(","," ")
	line = line.replace("'"," ")
	return line
	
	
def make_connection (ip,username,password):
	try:
		return netmiko.ConnectHandler(device_type='cisco_ios', ip=ip, username=username, password=password)
	except:
		try:
			return netmiko.ConnectHandler(device_type='cisco_ios_telnet', ip=ip, username=username, password=password)
		except:
			issue = ip+ ", can't be ssh/telneted to"
			to_doc_a("Issues.csv", issue)
			to_doc_a("Issues.csv", '\n')
			return None
			
def find_child_text (file, text):
	all = []
	parse = CiscoConfParse(file)
	for obj in parse.find_objects(text):
		each_obj = []
		each_obj.append(obj.text)
		for each in obj.all_children:
			each_obj.append(each.text)
		all.append(each_obj)
	return all
	
def remove_start(line,remove_this):
	line_search = re.search(remove_this,line)
	line = line[line_search.end():]
	return line

def find_hostname(net_connect):
	return net_connect.find_prompt()[:-1]
	
def send_command (net_connect, command):
	return net_connect.send_command_expect(command)