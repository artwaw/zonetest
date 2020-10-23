#!/usr/bin/env python3

import argparse
import dns.resolver
import dns.exception
import ipaddress

def isIP(param):
	try:
		test = ipaddress.ip_address(param)
		return True
	except:
		return False
	
params = argparse.ArgumentParser(description='Tester for after zone migration between servers.\nTakes a list of entries in the zone from zone file, queries old server and compares the output with given name server.',)
params.add_argument('zonefile', metavar='FileName', action='store', help='Zone file parsed for entries to be checked.')
params.add_argument('ns_server', metavar='NameServer', action='store', help='Target name server IP or URL')
params.add_argument('--coma', action='store_true', required=False, help='Use coma as delimeter. Otherwise TAB is used. Optional parameter')
args = params.parse_args()
if (args.coma):
	delimeter=','
else:
	delimeter='\t'
# Loading zone
try:
	zfile=open(args.zonefile)
except OSError as e:
	print(e.strerror+": "+e.filename)
	exit(e.errno)
print("File loaded.")
zone_content = []
targetNS = ''
if isIP(args.ns_server):
	targetNS = args.ns_server
else:
	ipRes = dns.resolver.Resolver()
	targetNS = str(ipRes.resolve(args.ns_server).response.answer[0][0])
if (targetNS == ''):
	print("Target name server given as URL ("+args.ns_server+") could not be resolved to IP address. Bailing out...")
	exit(1)
print("Target name server: "+targetNS)
sourceNS = ''
for line in zfile:
	if line.strip().startswith(';'):
		continue
	if 'SOA' in line:
		domain = line.split(delimeter)[0].removesuffix('.').strip()
		print('Detected domain: '+domain)
		continue;
	parts = line.split(delimeter)
	if len(parts) < 5:
		continue
	if parts[2].strip() == 'IN':
		if parts[0].strip() == '@' and parts[3].strip() == 'NS':
			if sourceNS == '':
				srcCandidate = parts[4].strip().removesuffix('.')
				if isIP(srcCandidate):
					sourceNS = srcCandidate
				else:
					ipRes = dns.resolver.Resolver()
					answer = ipRes.resolve(srcCandidate)
					sourceNS = str(answer.response.answer[0][0])
				if sourceNS == '':
					print("Source name server found as URL ("+parts[4].strip().removesuffix('.')+") could not be resolved to IP address. Bailing out...")
					exit(1)
				print("Found \"old\" name server: "+sourceNS)
			continue
		zone_content.append(line.strip())
zfile.close()
RTypes = {'A':1, 'A6':38, 'AAAA':28, 'AFSDB':18, 'ANY':255, 'APL':42, 'AVC':258, 'AXFR':252, 'CAA':257, 'CDNSKEY':60, 'CDS':59, 'CERT':37, 'CNAME':5, 'CSYNC':62, 'DHCID':49, 'DLV':32769, 'DNAME':39, 'DNSKEY':48, 'DS':43,
			'EUI48':108, 'EUI64':109, 'GPOS':27, 'HINFO':13, 'HIP':55, 'IPSECKEY':45, 'ISDN':20, 'IXFR':251, 'KEY':25, 'KX':36, 'LOC':29, 'MAILA':254, 'MAILB':253, 'MB':7, 'MD':3, 'MF':4, 'MG':8, 'MINFO':14, 'MR':9,
			'MX':15, 'NAPTR':35, 'NONE':0, 'NS':2, 'NSAP':22, 'NSEC':47, 'NSEC3':50, 'NSEC3PARAM':51, 'NULL':10, 'NXT':30, 'OPT':41, 'PTR':12, 'PX':26, 'RP':17, 'RRSIG':46, 'RT':21, 'SIG':24, 'SOA':6, 'SPF':99, 'SRV':33,
			'SSHFP':44, 'TA':32768, 'TKEY':249, 'TLSA':52, 'TSIG':250, 'TXT':16, 'UNSPEC':103, 'URI':256, 'WKS':11, 'X25':19}
# ALl vars known, setting up the dns resolvers
oldDNS = dns.resolver.Resolver()
oldDNS.nameservers = [ sourceNS ]
newDNS = dns.resolver.Resolver()
newDNS.nameservers = [ targetNS ]
# Good to go. Processing...
total = str(len(zone_content))
counter = 0;
print("Setup complete. Processing "+total+" entries...")
for line in zone_content:
	counter = counter+1
	parts = line.split(delimeter)
	print("Testing ("+str(counter)+"/"+total+") "+parts[3].strip()+" record "+parts[0].strip()+": ",end='')
	print(parts[0].strip()+"."+domain,end=' ')
	try:
		oldpart = oldDNS.resolve(parts[0].strip()+"."+domain,RTypes[parts[3].strip()]).response.answer[0][0]
	except dns.exception.DNSException as e:
		print("[FAILED - source DNS]")
		print(e.msg)
		continue
	try:
		newpart = newDNS.resolve(parts[0].strip()+'.'+domain,RTypes[parts[3].strip()]).response.answer[0][0]
	except dns.exception.DNSException as e:
		print("[FAILED - target DNS]")
		print(e.msg)
		continue
	if oldpart == newpart:
		print("[CORRECT]")
	else:
		print("[FAILED]")
		print("Old record: "+oldpart)
		print("New record: "+newpart)
print("Finished.")
