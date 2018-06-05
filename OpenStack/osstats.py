#!/usr/bin/env python3
import sys
import argparse
import os
from prettytable import PrettyTable
from keystoneauth1 import identity
from keystoneauth1 import session
from keystoneclient.v3 import client as keystoneClient
from novaclient import client as novaClient
from neutronclient.v2_0 import client as neutronClient

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

print("Check:")
print("\t 1 - hypervisor stats")
print("\t 2 - hypervisor servers")
print("\t 3 - floating ip pool")
sel = '2'
sel = input("Selection: ")
if sel == '1':
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
elif sel == '2':
    nova = novaClient.Client(version="2", session=sess)
    hypervisors = nova.hypervisors.list()
    print("Available hypervisors: ")
    i = 0
    for hv in hypervisors:
        print("{} - {}".format(i, hv.service["host"]))
        i += 1
    slhv = int(input("Select hypervisor: "))

    hypervisor = nova.hypervisors.search(hypervisors[slhv].service["host"], True)[0]
    serverslist = nova.servers.list(detailed="True", search_opts={'all_tenants': 1,
                                                                  'host': hypervisors[slhv].service["host"]})
    #projects = keystone.projects.list(domain='default')
    projects = keystone.projects.list()
    flavors = nova.flavors.list()
    outputtable = PrettyTable(['Instance name', 'Instance ID', 'Name', 'Status', 'Flavor', 'Project ID', 'Project description',
                               'Project name'])
    outputtable.align = "l"
    for server in serverslist:
        for project in projects:
            if server.tenant_id == project.id:
                for flavor in flavors:
                    if server.flavor['id'] == flavor.id:
                        flavorinfo = str(flavor.ram) + " MB; " + str(flavor.vcpus) + " vCPUs; " + flavor.name
                        outputtable.add_row([server.name, server.id, server._info['OS-EXT-SRV-ATTR:instance_name'], server.status, flavorinfo, project.id,
                                            project.description, project.name])
                        continue
                continue
    outputtable.sortby = 'Project name'
    if input("Detailed output [N/y]: ").lower() == 'y':
        print(outputtable)
    else:
        print(outputtable.get_string(fields=['Instance name', 'Instance ID', 'Status', 'Project name']))
else:
    neutron = neutronClient.Client(session=sess)
    print(neutron.list_networks({'name': 'route:external', 'boolean': True}))
    print(neutron.list_floatingips())
