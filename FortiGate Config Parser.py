"""
Fortinet Config Parse Tool v0.3

This tool is used to parse a Fortinet Fortigate configuration file into a human readable TSV format.

"""
import os.path
import re
import sys

# Create category ratings dictionary from the static file
ratings = {}
ratingFile = open('Categories.txt', 'r')
for line in ratingFile:
    tempLine = line.strip().split('=')
    if len(tempLine) > 1:
        ratings[tempLine[0]] = tempLine[1]
ratingFile.close()

confFile = open('config.conf', 'r')

count = len(open('config.conf', 'r').readlines())

configLine_re = re.compile('\W*?config (.*)\n')
endLine_re = re.compile('\s*?(end)\n')
finalEnd_re = re.compile('(end)\n')


def printLine(line, secType):
    tempFile = open(secType + '.txt', 'a')
    print(line[:-1], file=tempFile)
    tempFile.close()


# Read the configuration file, and sort out the appropriate sections.
# Use defined printing function to separate sections into their own files.
secType = ''
i = 0
for line in confFile:
    sys.stdout.write("\r")
    sys.stdout.write(
        "Parsing : " + str(int(100 * i / count)) + "% done (" + "line " + str(i) + " of " + str(count) + ")")
    i += 1
    if configLine_re.match(line) is not None:
        secType = (configLine_re.findall(line)[0])

    if secType == "firewall policy":
        if finalEnd_re.match(line) or configLine_re.match(line):
            continue
        printLine(line, secType)
    elif secType == "identity-based-policy":
        if endLine_re.match(line) is not None:
            secType = "firewall policy"
            printLine(line, secType)
            continue
        secType = "firewall policy"
        printLine(line, secType)
    elif secType == "firewall address":
        if finalEnd_re.match(line) or configLine_re.match(line):
            continue
        printLine(line, secType)
    elif secType == "firewall addrgrp":
        if finalEnd_re.match(line) or configLine_re.match(line):
            continue
        printLine(line, secType)
    elif secType == "firewall service custom":
        if finalEnd_re.match(line) or configLine_re.match(line):
            continue
        printLine(line, secType)
    elif secType == "firewall service group":
        if finalEnd_re.match(line) or configLine_re.match(line):
            continue
        printLine(line, secType)
    elif secType == "router static":
        if finalEnd_re.match(line) or configLine_re.match(line):
            continue
        printLine(line, secType)
    elif secType == "webfilter ftgd-local-cat":
        if finalEnd_re.match(line) or configLine_re.match(line):
            continue
        printLine(line, secType)
    elif secType == "webfilter ftgd-local-rating":
        if finalEnd_re.match(line) or configLine_re.match(line):
            continue
        printLine(line, secType)
    elif secType == "vpn ipsec phase2-interface":
        if finalEnd_re.match(line) or configLine_re.match(line):
            continue
        printLine(line, secType)
    elif secType == "vpn ipsec phase1-interface":
        if finalEnd_re.match(line) or configLine_re.match(line):
            continue
        printLine(line, secType)
    elif secType == "system interface":
        if finalEnd_re.match(line) or configLine_re.match(line):
            continue
        printLine(line, secType)
    elif secType == "router static":
        if finalEnd_re.match(line) or configLine_re.match(line):
            continue
        printLine(line, secType)
    else:
        continue
confFile.close()
sys.stdout.write('\n')

if not os.path.exists('output'):
    os.makedirs('output')

# Compiled regexes which will find specific key/value pairs - likely not necessary to have one of each
srcint_re = re.compile('set srcintf "(.*?)"')
name_re = re.compile('set name "(.*?)"')
dstint_re = re.compile('set dstintf "(.*?)"')
srcaddr_re = re.compile('set srcaddr (".*")')
dstaddr_re = re.compile('set dstaddr (".*")')
action_re = re.compile('set action (.*?)\n')
schedule_re = re.compile('set schedule (".*")')
svc_re = re.compile('set service (".*")')
utmstatus_re = re.compile('set utm-status (.*?)\n')
logtraffic_re = re.compile('set logtraffic (.*?)\n')
applist_re = re.compile('set application-list (".*")')
avprofile_re = re.compile('set av-profile (".*")')
webfilterprofile_re = re.compile('set webfilter-profile (".*")')
ipssensor_re = re.compile('set ips-sensor (".*")')
sslportal_re = re.compile('set sslvpn-portal (".*")')
ppo_re = re.compile('set profile-protocol-options (".*")')
dio_re = re.compile('set deep-inspection-options (".*")')
nat_re = re.compile('set nat (.*?)\n')
fsso_re = re.compile('set fsso (.*?)\n')
group_re = re.compile('set groups (.*?)\n')
identitybased_re = re.compile('set identity-based (.*?)\n')
comments_re = re.compile('set comments (".*")')
sslcipher_re = re.compile('set sslvpn-cipher (.*?)\n')
ippool_re = re.compile('set ippool (.*?)\n')
status_re = re.compile('set status (.*?)\n')
poolname_re = re.compile('set poolname "(.*?)"\n')

if os.path.isfile("firewall policy.txt"):
    print("Firewall policies...", flush=True)
    file = open('firewall policy.txt', 'r')
    policyfile = open('output/policy.tsv', 'w+')

    # Print the header row for our TSV file, and initialize the variables used.
    print(
        "Rule #\tName\tSource Interface\tDestination Interface\tSources\tDestinations\tIdentity Based\tServices\tAction\tSchedule\tLog Traffic\tNAT\tIP-Pool\tPoolName\tUTM-Status\tFSSO\tGroups\tApplicaiton List\tAV Profile\tWebfilter Profile\tIPS Sensor\tProfile Protocol\tDeep Inspection\tSSL-Cipher\tSSL-Portal\tStatus\tComments",
        file=policyfile)
    rule = srcint = dstint = srcaddrStr = dstaddrStr = ident = svcStr = action = schedule = utm = log = groupStr = appList = av = web = ips = ppo = dio = nat = fsso = comment = sslPortal = sslCipher = ippool = status = poolname = ''

    # Begin looping through each line. We will grouping policies together based on the 'edit' and 'next' keywords - with an exception for identity based policies (which should be 'nested' in the spreadsheet)
    for line in file:
        # check for conditions which trigger the current line to print, and then reset all variables.
        # We want identity based policies on their own line, the phrase 'config identity-based-policy' can trigger this.
        if ("next" in line) or ("config identity-based-policy" in line):
            # Stops an extra line from being printed after identity based sections
            if rule == '':
                continue
            print(
                "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s" % (
                    rule, name, srcint, dstint, srcaddrStr, dstaddrStr, ident, svcStr, action, schedule, log, nat, ippool,
                    poolname, utm, fsso, groupStr, appList, av, web, ips, ppo, dio, sslCipher, sslPortal, status, comment),
                file=policyfile)
            name = rule = srcint = dstint = srcaddrStr = dstaddrStr = ident = svcStr = action = schedule = utm = log = groupStr = appList = av = web = ips = ppo = dio = nat = fsso = comment = sslPortal = sslCipher = ippool = status = poolname = ''
            continue
        # Find the policy number being worked on
        newRule = re.search("edit ([0-9]+.*?)\n", line)
        if newRule:
            rule = newRule.group(1)
            continue

        # Begin checking what key/value this line contains (if not one of the 'processing' keys from above.) If one is found, evaluate it, and stop checking - moving onto the next line in the file.
        # *******NOTE: SOME PROPERTY TYPES MAY BE MISSING IF I'M NOT AWARE OF THEM*******
        # Some of these may return multiple values; If so, they are enumerated and compiled into a comma separated string.
        if "set name" in line:
            tmp = name_re.findall(line)
            name = tmp[0]
            continue
        if "set srcintf" in line:
            tmp = srcint_re.findall(line)
            srcint = tmp[0]
            continue
        if "set dstintf" in line:
            tmp = dstint_re.findall(line)
            dstint = tmp[0]
            continue
        if "set srcaddr" in line:
            srcaddr = srcaddr_re.findall(line)
            srcaddrStr = ''.join(map(str, srcaddr))
            srcaddrStr = srcaddrStr.replace('"', '')
            continue
        if "set dstaddr" in line:
            dstaddr = dstaddr_re.findall(line)
            dstaddrStr = ''.join(map(str, dstaddr))
            dstaddrStr = dstaddrStr.replace('"', '')
            continue
        if "set action" in line:
            tmp = (action_re.findall(line)[0])
            action = tmp
            continue
        if "set schedule" in line:
            tmp = (schedule_re.findall(line)[0])
            schedule = tmp[1:-1]
            continue
        if "set service" in line:
            svc = svc_re.findall(line)
            svcStr = ''.join(map(str, svc))
            svcStr = svcStr.replace('"', '')
            continue
        if "set logtraffic" in line:
            log = (logtraffic_re.findall(line)[0])
            continue
        if "set nat" in line:
            nat = (nat_re.findall(line)[0])
            continue
        if "set utm-status" in line:
            utm = (utmstatus_re.findall(line)[0])
            continue
        if "application-list" in line:
            appList = (applist_re.findall(line)[0])
            appList = appList[1:-1]
            continue
        if "profile-protocol-options" in line:
            ppo = (ppo_re.findall(line)[0])
            ppo = ppo[1:-1]
            continue
        if "set comments" in line:
            # comment = (comments_re.findall(line)[0])
            # comment = comment[1:-1]
            continue
        if "set av-profile" in line:
            av = (avprofile_re.findall(line)[0])
            av = av[1:-1]
            continue
        if "set ips-sensor" in line:
            ips = (ipssensor_re.findall(line)[0])
            ips = ips[1:-1]
            continue
        if "set webfilter-profile" in line:
            web = (webfilterprofile_re.findall(line)[0])
            web = web[1:-1]
        if "set deep-inspection-options" in line:
            dio = (dio_re.findall(line)[0])
            dio = dio[1:-1]
            continue
        if "set identity-based" in line:
            ident = (identitybased_re.findall(line)[0])
            continue
        if "config identity-based-policy" in line:
            continue
        if "set groups" in line:
            groups = group_re.findall(line)
            groupStr = ''.join(map(str, groups))
            groupStr = groupStr.replace('"', '')
            continue
        if "set sslvpn-portal" in line:
            sslPortal = (sslportal_re.findall(line)[0])
            sslPortal = sslPortal[1:-1]
            continue
        if "set sslvpn-cipher" in line:
            sslCipher = (sslcipher_re.findall(line)[0])
            continue
        if "set fsso" in line:
            fsso = (fsso_re.findall(line)[0])
            continue
        if "set ippool" in line:
            ippool = (ippool_re.findall(line)[0])
            continue
        if "set status" in line:
            status = (status_re.findall(line)[0])
            continue
        if "set poolname" in line:
            poolame = (poolname_re.findall(line)[0])
            # print(poolname)
            continue
    file.close()
    policyfile.close()
    os.remove('firewall policy.txt')

type_re = re.compile('set type (.*?)\n')
endIP_re = re.compile('set end-ip (\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3})')
startIP_re = re.compile('set start-ip (\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3})')
subnet_re = re.compile('set subnet (\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3} \d{1,3}.\d{1,3}.\d{1,3}.\d{1,3})')
interface_re = re.compile('set associated-interface "(.*?)"')
comment_re = re.compile('set comment "(.*?)"\n')
fqdn_re = re.compile('set fqdn "(.*?)"\n')

if os.path.exists("firewall address.txt"):
    print("Firewall Addresses...", flush=True)
    file = open('firewall address.txt', 'r')
    addrFile = open('output/addresses.tsv', 'w+')

    print("Address\tType\tSubnet\tInterface\tFQDN\tStart IP\tEnd IP\tComment", file=addrFile)
    addr = addrInt = addrType = endIP = startIP = subnet = fqdn = comment = ""

    for line in file:
        if "next" in line:
            print("%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s" % (addr, addrType, subnet, addrInt, fqdn, startIP, endIP, comment),
                  file=addrFile)
            addr = addrInt = addrType = endIP = startIP = subnet = fqdn = comment = ""
            continue
        newAddr = re.search('edit "(.*?)"\n', line)
        if newAddr:
            addr = newAddr.group(1)
            continue
        if "set associated-interface" in line:
            tmp = interface_re.findall(line)
            addrInt = tmp[0]
            continue
        if "set type" in line:
            tmp = type_re.findall(line)
            addrType = tmp[0]
            continue
        if "set end-ip" in line:
            tmp = endIP_re.findall(line)
            endIP = tmp[0]
            continue
        if "set start-ip" in line:
            tmp = startIP_re.findall(line)
            startIP = tmp[0]
            continue
        if "set fqdn" in line:
            tmp = fqdn_re.findall(line)
            fqdn = tmp[0]
            continue
        if "set comment" in line:
            tmp = comment_re.findall(line)
            comment = tmp[0]
            continue
        if "set subnet" in line:
            tmp = subnet_re.findall(line)
            subnet = tmp[0]
            continue
    file.close()
    addrFile.close()
    os.remove('firewall address.txt')

# Address Groups
member_re = re.compile('set member (.*?)\n')
if os.path.exists("firewall addrgrp.txt"):
    print("Firewall Addresses Groups...", flush=True)
    file = open('firewall addrgrp.txt', 'r')
    groupFile = open('output/groups.tsv', 'w+')

    print("Group\tMembers", file=groupFile)
    group = ""

    for line in file:
        if "next" in line:
            print("%s\t%s" % (group, member), file=groupFile)
            group = ""
            continue
        newGroup = re.search('edit "(.*?)"\n', line)
        if newGroup:
            group = newGroup.group(1)
            continue
        if "set member" in line:
            member = (member_re.findall(line)[0])
            member = member.replace('"', '')
            member = member.replace(' ', '\t')
    file.close()
    groupFile.close()
    os.remove('firewall addrgrp.txt')

# Static Routes

dst_re = re.compile('set dst (.*?)\n')
gateway_re = re.compile('set gateway (.*?)\n')
priority_re = re.compile('set priority (.*?)\n')
device_re = re.compile('set device (.*?)\n')
dst_addr_re = re.compile('set dstaddr (.*?)\n')
blackhole_re = re.compile('set blackhole (.*?)\n')
distance_re = re.compile('set distance (.*?)\n')
comment_re = re.compile('set comment (.*?)\n')

if os.path.exists("router static.txt"):
    print("Static Routes...", flush=True)
    file = open('router static.txt', 'r')
    staticFile = open('output/static.tsv', 'w+')

    print(
        "Destination\tGateway\tPriority\tDevice\tDestination Address\tBlackhole\tDistance\tComment",
        file=staticFile)
    destination = gateway = priority = device = dst_addr = blackhole = distance = comment = ""

    for line in file:
        if "next" in line:
            print("%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s" % (
                destination, gateway, priority, device, dst_addr, blackhole, distance, comment), file=staticFile)
            destination = gateway = priority = device = dst_addr = blackhole = distance = comment = ""
            continue
        newStatic = re.search('edit "(.*?)"\n', line)
        if newStatic:
            name = newStatic.group(1)
            continue
        if "set dst " in line:
            tmp = dst_re.findall(line)
            destination = tmp[0]
            continue
        if "set gateway" in line:
            tmp = gateway_re.findall(line)
            gateway = tmp[0]
            continue
        if "set priority" in line:
            tmp = priority_re.findall(line)
            priority = tmp[0]
            continue
        if "set device" in line:
            tmp = device_re.findall(line)
            device = tmp[0]
            continue
        if "set dstaddr" in line:
            tmp = dst_addr_re.findall(line)
            dst_addr = tmp[0]
            continue
        if "set blackhole" in line:
            tmp = blackhole_re.findall(line)
            blackhole = tmp[0]
            continue
        if "set distance" in line:
            tmp = distance_re.findall(line)
            distance = tmp[0]
            continue
        if "set comment" in line:
            tmp = comment_re.findall(line)
            comment = tmp[0]
            continue
    file.close()
    staticFile.close()
    os.remove("router static.txt")

# Add local categories to ratings dictionary
catID_re = re.compile('set id (.*?)\n')
if os.path.exists("webfilter ftgd-local-cat.txt"):
    print("Webfiltering Categories...", flush=True)
    file = open("webfilter ftgd-local-cat.txt")

    for line in file:
        if "next" in line:
            ratings[ID] = cat
        newCat = re.search('edit "(.*?)"\n', line)
        if newCat:
            cat = newCat.group(1)
            continue
        if "set id" in line:
            ID = (catID_re.findall(line)[0])
    file.close()
    os.remove("webfilter ftgd-local-cat.txt")

# Web rating overrides
ratingID_re = re.compile('set rating (.*?)\n')
if os.path.exists("webfilter ftgd-local-rating.txt"):
    print("Webfiltering Ratings...", flush=True)
    file = open("webfilter ftgd-local-rating.txt", 'r')
    ratingFile = open('output/ratings.tsv', 'w+')

    print("URL\tOverride Category", file=ratingFile)

    for line in file:
        if "next" in line:
            print("%s\t%s" % (url, rating), file=ratingFile)
        newURL = re.search('edit "(.*?)"\n', line)
        if newURL:
            url = newURL.group(1)
            continue
        if "set rating" in line:
            ID = (ratingID_re.findall(line)[0])
            rating = ratings[ID]
    file.close()
    ratingFile.close()
    os.remove("webfilter ftgd-local-rating.txt")

# IPSec Tunnels

p1_re = re.compile('set phase1name (.*?)\n')
srcName_re = re.compile('set src-name (.*?)\n')
dstName_re = re.compile('set dst-name (.*?)\n')
srcSubnet_re = re.compile('set src-subnet (.*?)\n')
dstSubnet_re = re.compile('set dst-subnet (.*?)\n')
encrypt_re = re.compile('set proposal (.*?)\n')
keylife_re = re.compile('set keylifeseconds (.*?)\n')
keepalive_re = re.compile('set keepalive (.*?)\n')
autonego_re = re.compile('set auto-negotiate (.*?)\n')
pfs_re = re.compile('set pfs (.*?)\n')
dhgrp_re = re.compile('set dhgrp (.*?)\n')
replay_re = re.compile('set replay (.*?)\n')
psk_re = re.compile('set psksecret ENC (.*?)\n')
remotegw_re = re.compile('set remote-gw (.*?)\n')
netdevice_re = re.compile('set net-device (.*?)\n')

if os.path.exists("vpn ipsec phase2-interface.txt"):
    print("VPN Phase 2...", flush=True)
    file = open('vpn ipsec phase2-interface.txt', 'r')
    p2File = open('output/phase2.tsv', 'w+')

    print(
        "Phase2\tP1\tSrc Name\tDst Name\tSrc Subnet\tDst Subnet\tProposal\tKeylife\tKeep Alive?\tAuto-Negotiate?\tPFS?\tDH Group\tReplay Detection",
        file=p2File)
    name = p1 = srcName = dstName = encrypt = keylife = keepalive = autonego = pfs = dhgrp = replay = ""

    for line in file:
        if "next" in line:
            print("%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s" % (
                name, p1, srcName, dstName, srcSubnet, dstSubnet, encrypt, keylife, keepalive, autonego, pfs, dhgrp, replay), file=p2File)
            name = p1 = srcName = dstName = srcSubnet = dstSubnet = encrypt = keylife = keepalive = autonego = pfs = dhgrp = replay = ""
            continue
        newP2 = re.search('edit "(.*?)"\n', line)
        if newP2:
            name = newP2.group(1)
            continue
        if "set phase1name" in line:
            tmp = p1_re.findall(line)
            p1 = tmp[0]
            continue
        if "set src-name" in line:
            tmp = srcName_re.findall(line)
            srcName = tmp[0]
            continue
        if "set dst-name" in line:
            tmp = dstName_re.findall(line)
            dstName = tmp[0]
            continue
        if "set src-subnet" in line:
            tmp = srcSubnet_re.findall(line)
            srcSubnet = tmp[0]
            continue
        if "set dst-subnet" in line:
            tmp = dstSubnet_re.findall(line)
            dstSubnet = tmp[0]
            continue
        if "set proposal" in line:
            tmp = encrypt_re.findall(line)
            encrypt = tmp[0]
            continue
        if "set keylifeseconds" in line:
            tmp = keylife_re.findall(line)
            keylife = tmp[0]
            continue
        if "set keepalive" in line:
            tmp = keepalive_re.findall(line)
            keepalive = tmp[0]
            continue
        if "set auto-negotiate" in line:
            tmp = autonego_re.findall(line)
            autonego = tmp[0]
            continue
        if "set pfs" in line:
            tmp = pfs_re.findall(line)
            pfs = tmp[0]
            continue
        if "set dhgrp" in line:
            tmp = dhgrp_re.findall(line)
            dhgrp = tmp[0]
            continue
        if "set replay" in line:
            tmp = replay_re.findall(line)
            replay = tmp[0]
            continue
    file.close()
    p2File.close()
    os.remove('vpn ipsec phase2-interface.txt')

if os.path.exists("vpn ipsec phase1-interface.txt"):
    print("VPN Phase 1...", flush=True)
    file = open('vpn ipsec phase1-interface.txt', 'r')
    p1File = open('output/phase1.tsv', 'w+')

    print("Phase1\tNet Device\tProposal\tDH Group\tRemote Gateway\tPSK", file=p1File)
    name = encrypt = netdevice = psksec = dhgrp = remotegw = ""

    for line in file:
        if "next" in line:
            print("%s\t%s\t%s\t%s\t%s\t%s" % (name, netdevice, encrypt, dhgrp, remotegw, psksec), file=p1File)
            name = netdevice = encrypt = remotegw = pksec = dhgrp = replay = ""
            continue
        newP1 = re.search('edit "(.*?)"\n', line)
        if newP1:
            name = newP1.group(1)
            continue
        if "set phase1name" in line:
            tmp = p1_re.findall(line)
            p1 = tmp[0]
            continue
        if "set proposal" in line:
            tmp = encrypt_re.findall(line)
            encrypt = tmp[0]
            continue
        if "set psksecret" in line:
            tmp = psk_re.findall(line)
            psksec = tmp[0]
            continue
        if "set dhgrp" in line:
            tmp = dhgrp_re.findall(line)
            dhgrp = tmp[0]
            continue
        if "set remote-gw" in line:
            tmp = remotegw_re.findall(line)
            remotegw = tmp[0]
            continue
        if "set net-device" in line:
            tmp = netdevice_re.findall(line)
            netdevice = tmp[0]
            continue
    file.close()
    p1File.close()
    os.remove('vpn ipsec phase1-interface.txt')

# Interfaces

mode_re = re.compile('set mode (.*?)\n')
ip_re = re.compile('set ip (.*?) (.*?)\n')
access_re = re.compile('set allowaccess (.*?)\n')
type_re = re.compile('set type (.*?)\n')
alias_re = re.compile('set alias (.*?)\n')
password_re = re.compile('set password (.*?)\n')
username_re = re.compile('set username (.*?)\n')
unnumbered_re = re.compile('set ipunnumbered (.*?)\n')
vlanid_re = re.compile('set vlanid (.*?)\n')
superint_re = re.compile('set interface (.*?)\n')
dhcp_ip_re = re.compile('set dhcp-relay-ip (.*?)\n')
dhcp_relay_re = re.compile('set dhcp-relay-service (.*?)\n')
stp_re = re.compile('set stp (.*?)\n')
security_re = re.compile('set security-mode (.*?)\n')
desc_re = re.compile('set description (.*?)\n')
devid_re = re.compile('set device-identification (.*?)\n')
role_re = re.compile('set role (.*?)\n')

if os.path.exists("system interface.txt"):
    print("Interfaces...", flush=True)
    file = open('system interface.txt', 'r')
    interfaceFile = open('output/interfaces.tsv', 'w+')

    print("Interface\tType\tIP\tVLAN ID\tSuper Interface\tAccess\tAlias\tRole\tComment\tDevice Identification\tDescription\tSecurity Mode\tSpanning Tree\tDHCP Relay\tDHCP Relay IP\tIP Unnumbered\tUsername\tPassword", file=interfaceFile)
    mode = ip = access = type = alias = password = username = unnumbered = vlanid = superint = dhcp_ip = dhcp_relay = stp = security = desc = devid = role = ""

    for line in file:
        if "next" in line:
            print("%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s" % (interface, type, ip, vlanid, superint, access, alias, role, comment, devid, desc, security, stp, dhcp_relay, dhcp_ip, unnumbered, username, password),
                  file=interfaceFile)
            mode = ip = access = type = alias = password = username = unnumbered = vlanid = superint = dhcp_ip = dhcp_relay = stp = security = desc = devid = role = ""
            continue
        newInt = re.search('edit "(.*?)"\n', line)
        if newInt:
            interface = newInt.group(1)
            continue
        if "set mode" in line:
            tmp = mode_re.findall(line)
            mode = tmp[0]
            continue
        if "set ip " in line:
            tmp = ip_re.findall(line)
            ip = tmp[0][0]
            ipmask = tmp[0][1]
            continue
        if "set allowaccess" in line:
            tmp = access_re.findall(line)
            access = tmp[0]
            continue
        if "set type" in line:
            tmp = type_re.findall(line)
            type = tmp[0]
            continue
        if "set alias" in line:
            tmp = alias_re.findall(line)
            alias = tmp[0]
            continue
        if "set role" in line:
            tmp = role_re.findall(line)
            role = tmp[0]
            continue
        if "set device-identification " in line:
            tmp = devid_re.findall(line)
            devid = tmp[0]
            continue
        if "set description" in line:
            tmp = desc_re.findall(line)
            desc = tmp[0]
            continue
        if "set security-mode" in line:
            tmp = security_re.findall(line)
            security = tmp[0]
            continue
        if "set stp" in line:
            tmp = stp_re.findall(line)
            stp = tmp[0]
            continue
        if "set dhcp-relay-service" in line:
            tmp = dhcp_relay_re.findall(line)
            dhcp_relay = tmp[0]
            continue
        if "set dhcp-relay-ip" in line:
            tmp = dhcp_ip_re.findall(line)
            dhcp_ip = tmp[0]
            continue
        if "set interface" in line:
            tmp = superint_re.findall(line)
            superint = tmp[0]
            continue
        if "set vlanid" in line:
            tmp = vlanid_re.findall(line)
            vlanid = tmp[0]
            continue
        if "set ipunnumbered" in line:
            tmp = unnumbered_re.findall(line)
            unnumbered = tmp[0]
            continue
        if "set username" in line:
            tmp = username_re.findall(line)
            username = tmp[0]
            continue
        if "set password" in line:
            tmp = password_re.findall(line)
            password = tmp[0]
            continue
    file.close()
    staticFile.close()
    os.remove("system interface.txt")
    
# Services

category_re = re.compile('set category (.*?)\n')
tcprange_re = re.compile('set tcp-portrange (.*?)\n')
udprange_re = re.compile('set udp-portrange (.*?)\n')
protocol_re = re.compile('set protocol (.*?)\n')
protocolnumber_re = re.compile('set protocol-number (.*?)\n')
visibility_re = re.compile('set visibility (.*?)\n')

if os.path.exists("firewall service custom.txt"):
    print("Services...", flush=True)
    file = open('firewall service custom.txt', 'r')
    interfaceFile = open('output/services.tsv', 'w+')

    print("Service\tCategory\tTCP ports\tUDP ports\tProtocol\tProtocol Number\tVisibility\t", file=interfaceFile)
    service = category = tcprange = udprange = protocol = protocolnumber = visibility = ""

    for line in file:
        if "next" in line:
            print("%s\t%s\t%s\t%s\t%s\t%s\t%s" % (service, category, tcprange, udprange, protocol, protocolnumber, visibility),
                  file=interfaceFile)
            service = category = tcprange = udprange = protocol = protocolnumber = visibility = ""
            continue
        newService = re.search('edit "(.*?)"\n', line)
        if newService:
            service = newService.group(1)
            continue
        if "set category" in line:
            tmp = category_re.findall(line)
            category = tmp[0]
            continue
        if "set tcp-portrange" in line:
            tmp = tcprange_re.findall(line)
            tcprange = tmp[0].replace(" ", ", ")
            continue
        if "set udp-portrange" in line:
            tmp = udprange_re.findall(line)
            udprange = tmp[0].replace(" ", ", ")
            continue
        if "set protocol " in line:
            tmp = protocol_re.findall(line)
            protocol = tmp[0]
            continue
        if "set protocol-number" in line:
            tmp = protocolnumber_re.findall(line)
            protocolnumber = tmp[0]
            continue
        if "set visibility" in line:
            tmp = visibility_re.findall(line)
            visibility = tmp[0]
            continue
        
    file.close()
    staticFile.close()
    os.remove("firewall service custom.txt")
    
# Groupes de Services

members_re = re.compile('set member (.*?)\n')


if os.path.exists("firewall service group.txt"):
    print("Service Groups...", flush=True)
    file = open('firewall service group.txt', 'r')
    interfaceFile = open('output/servicegroups.tsv', 'w+')

    print("Service\tMembers\t", file=interfaceFile)
    group = members = ""

    for line in file:
        if "next" in line:
            print("%s\t%s" % (group, members),
                  file=interfaceFile)
            group = members = ""
            continue
        newGroup = re.search('edit "(.*?)"\n', line)
        if newGroup:
            group = newGroup.group(1)
            continue
        if "set member" in line:
            tmp = members_re.findall(line)
            members = tmp[0].replace("\"", "").replace(" ", ", ")
            continue
        
        
    file.close()
    staticFile.close()
    os.remove("firewall service group.txt")