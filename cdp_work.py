from common_functions import *
import netmiko
import time
from getpass import getpass
from ciscoconfparse import CiscoConfParse
from pprint import pprint
from common_functions import *

def cdpNeighbors(txt):
    fields = [ ('deviceId', r'Device ID:\s*([\w\._-]+)'),
               ('ipAddress', r'IP(?:v4)? Address: (\d+\.\d+\.\d+\.\d+)'),
               ('platform', r'Platform: (\w[^,\r\n]*\w|\w)'),
               ('capabilities', r'Capabilities: (\w[^,\r\n]*\w|\w)'),
               ('localInterface', r'Interface: (\w[^,\r\n]*\w|\w)'),
               ('interface', r'Port ID \(outgoing port\): (\w[^,\r\n]*\w|\w)'),
               ('version', r'Version\s*:\s*\r?\n(\w[^\r\n]*)'),
               ('vtpDomain', r"VTP Management Domain(?: Name)?: '?(\w+)'?"),
               ('nativeVlan', r'Native VLAN: (\d+)'),
               ('duplex', r'Duplex: (\w[^\r\n]*\w|\w)')]
    for rawNeighbor in (n.group(1) for n in re.finditer(r'-{10,100}((?:.(?!-{10})){10,1500})', txt, re.S)):
        parsedNeighbor = dict()
        for label, exp in fields:
            m = re.search(exp, rawNeighbor, re.I)
            if m:
                parsedNeighbor[label] = m.group(1)
        if parsedNeighbor:
            yield parsedNeighbor

	
def fix_for_ciscoconfparse(file_name):
	cdp = read_doc(file_name)
	cdp_str = ""
	for line in cdp:
		
		if "---" not in line:
			line = "     "+line
		cdp_str = cdp_str+line
		#print (cdp_str)
	to_doc_w(file_name, cdp_str)

def parse_cdp_out(file_name):
	cdp_parse = {}
	fix_for_ciscoconfparse(file_name)
	cdp_doc=CiscoConfParse(file_name)
	strip_these = ("[","]","'", "")
	cdp_entries = cdp_doc.find_objects("-----")
	all_cdp_entries = []
	for cdp_entrie in cdp_entries:
		next_line = False
		cdp_parse = {}
		for cdp_line in cdp_entrie.all_children:
			if "IP a" in cdp_line.text:
				ip = get_ip(cdp_line.text)[0]
				cdp_parse['remote_ip'] = ip
				
			if "Device ID:" in cdp_line.text:
				id_start = str(cdp_line.text).find(":")+2
				remote_id = str(cdp_line.text)[id_start:]
				cdp_parse['remote_id'] = remote_id
			if "Platform: " in cdp_line.text:
				platform_start = str(cdp_line.text).find(":")+2
				tmp = str(cdp_line.text)[platform_start:]
				platform_end = tmp.find(",")
				platform = tmp[:platform_end]
				cdp_parse['platform'] = platform
			if "Capabilities: " in cdp_line.text:
				capabilities_start = str(cdp_line.text).find("Capabilities:")+14
				capabilities = str(cdp_line.text)[capabilities_start:]
				cdp_parse['capabilities'] = capabilities
			if "Interface: " in cdp_line.text:
				interface_start = str(cdp_line.text).find(":")+2
				interface_end = str(cdp_line.text).find(",")
				local_int = str(cdp_line.text)[interface_start:interface_end]
				cdp_parse['local_int'] = local_int
			if "Port ID (outgoing port): " in cdp_line.text:
				interface_start = str(cdp_line.text).find("Port ID (outgoing port):")+25
				remote_int = str(cdp_line.text)[interface_start:]
				cdp_parse['remote_int'] = remote_int	
	
			if next_line == True:
				version = str(cdp_line.text).lstrip(' ')
				cdp_parse['version'] = version
				next_line = False
				
			if "Version :" in cdp_line.text:
				next_line = True
				
			
		all_cdp_entries.append(cdp_parse)
	return all_cdp_entries

def tie_cdp_and_interface_dict_info(interface_dict,all_cdp_entries):
	for interface in interface_dict:
		for cdp_entrie in all_cdp_entries:
		#	print (interface["name"])
		#	print (cdp_entrie['local_int'])
			if interface["name"]== cdp_entrie['local_int']:
		#		print ("True")
				try:
					interface['remote_ip']		= cdp_entrie['remote_ip']
				except:
					pass
				try:
					interface['remote_id']		= cdp_entrie['remote_id']
				except:
					pass
				try:
					interface['platform']		= cdp_entrie['platform']
				except:
					pass
				try:
					interface['capabilities']	= cdp_entrie['capabilities']
				except:
					pass
				try:
					interface['remote_int']	= cdp_entrie['remote_int']
				except:
					pass
	return interface_dict
	return interface_dict
	
	