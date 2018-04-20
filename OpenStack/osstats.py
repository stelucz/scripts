#!/usr/bin/env python3
import sys
import argparse
import os
from prettytable import PrettyTable
from keystoneauth1 import identity
from keystoneauth1 import session
from keystoneclient.v3 import client as keystoneClient
from novaclient import client as novaClient

parser = argparse.ArgumentParser()
parser.add_argument('-deo', help='Don\'t do endpoint override', action='store_true')
args, unknown = parser.parse_known_args()

try:
    username = os.environ['OS_USERNAME']
    password = os.environ['OS_PASSWORD']
    project_name = os.environ['OS_PROJECT_NAME']
    project_domain_name = os.environ['OS_USER_DOMAIN_NAME']
    user_domain_name = os.environ['OS_USER_DOMAIN_NAME']
    auth_url = os.environ['OS_AUTH_URL']
except Exception as e:
    print("Environment variable: " + str(e) + " not found. EXITING \n")
    exit(1)

auth = identity.Password(auth_url=auth_url,
                         username=username,
                         password=password,
                         project_name=project_name,
                         project_domain_name=project_domain_name,
                         user_domain_name=user_domain_name)
sess = session.Session(auth=auth)

try:
    if args.deo:
        keystone = keystoneClient.Client(session=sess)
    else:
        keystone = keystoneClient.Client(session=sess,
                                         endpoint_override=auth_url)
except Exception as e:
    print("Keystone client could not be initialized. EXITING \n" + str(e))
    exit(1)

nova = novaClient.Client(version="2", session=sess)

outputtable = PrettyTable(['Hypervisor', 'ID', 'State', 'Status', 'Free RAM', 'Total RAM', 'Used RAM', 'vCPUs',
                           'Used vCPUs', 'Runnning VMs'])

hypervisors = nova.hypervisor_stats.statistics()
hypervisors_list = nova.hypervisors.list()
print(hypervisors_list)
for hv in hypervisors_list:
    outputtable.add_row([hv.hypervisor_hostname, hv.id, hv.state, hv.status, hv.free_ram_mb, hv.memory_mb,
                         hv.memory_mb_used, hv.vcpus, hv.vcpus_used, hv.running_vms])
outputtable.add_row(["TOTAL", "--", "--", "--", hypervisors.free_ram_mb,
                     hypervisors.memory_mb, hypervisors.memory_mb_used, hypervisors.vcpus, hypervisors.vcpus_used,
                     hypervisors.running_vms])
print(outputtable)
