#!/usr/bin/env python3
"""
Single file script for creating OpenStack users.

Single user can be created by calling script with positional arguments.
~# oscreateuser.py jdoe doe@mail.com "John Doe"

Batch of users can be created from file, with selected separator.
Users file with `;` separator.
user1;mail@mail1.com;John Doe
user2;mail@mail2.com;Foo Bar
~# oscreateuser.py -l users
"""

import sys
import argparse
import getpass
import os
import random
import string
from keystoneauth1 import identity
from keystoneauth1 import session
from keystoneclient.v3 import client as keystoneClient


def printuser(name, email, description, password):
    template = '''
Hello,

your OpenStack/SwiftStack account has been created.

User name: {0}
User password: {1}
URL: 
Domain: Default
    '''
    print("-----------------------------------------------------------------------------------------------------------")
    print("Username: " + name + " e-mail: " + email + " Description: " + description + " Password: " + password)
    print("Mail message to :" + email)
    print(template.format(name, password))
    print("-----------------------------------------------------------------------------------------------------------")


parser = argparse.ArgumentParser()
parser.add_argument('username', help='Username (login)', nargs='?')
parser.add_argument('email', help='E-mail address', nargs='?')
parser.add_argument('description', help='Description', nargs='?')
parser.add_argument('-deo', help='Don\'t do endpoint override', action='store_true')
parser.add_argument('-l', help='Users list. Format username email description. Selectable separator. One entry per row.')
args, unknown = parser.parse_known_args()


def grantroles(user, projects, roles):
    projects = projects.replace(" ", "").split(',')
    roles = roles.replace(" ", "").split(',')
    for project in projects:
        ksproj = keystone.projects.list(name=project)
        if not ksproj:
            print("Project with name " + project + " does not exist!")
        else:
            for role in roles:
                ksrole = keystone.roles.list(name=role)
                if not ksrole:
                    print("Role with name " + role + " does not exist!")
                else:
                    ksgrant = keystone.roles.grant(role=ksrole[0], user=user, project=ksproj[0])


try:
    username = os.environ['OS_USERNAME']
    password = os.environ['OS_PASSWORD']
    project_name = os.environ['OS_PROJECT_NAME']
    project_domain_name = os.environ['OS_USER_DOMAIN_NAME']
    user_domain_name = os.environ['OS_USER_DOMAIN_NAME']
    auth_url = os.environ['OS_AUTH_URL']
except Exception as e:
    print("Missing environment variable " + str(e) + " ! EXITING.")
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
        keystone = keystoneClient.Client(session=sess, endpoint_override=auth_url)
except Exception as e:
    print("Keystone client could not be initialized. EXITING \n" + str(e))
    exit(1)

if args.username and not args.l:
    password = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(12))
    try:
        ks = keystone.users.create(name=args.username, email=args.email, description=args.description,
                                   password=password)
        pom = input("Grant roles to user/s on projects? [Y/n]: ")
        if pom.lower() == 'y' or pom == '':
            projects = input("Enter project/s separated with ',': ")
            roles = input("Enter role/s separated with ',': ")
            grantroles(ks, projects, roles)
        printuser(args.username, args.email, args.description, password)
    except Exception as e:
        print("Creation of user " + args.username + " failed: " + str(e))
elif args.l:
    users = []
    if os.path.exists(os.path.join(args.l)):
        print('Using users list from file: ' + args.l)
        list = open(args.l, mode='r')
        sep = input('Type separator between values: ')
        pom = input("Grant roles to user/s on projects? [Y/n]: ")
        if pom.lower() == 'y' or pom == '':
            projects = input("Enter project/s separated with ',': ")
            roles = input("Enter role/s separated with ',': ")
        for line in list:
            parsedline = line.strip('\n').split(sep)
            users.append(parsedline)
            password = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(12))
            try:
                ks = keystone.users.create(name=parsedline[0], email=parsedline[1], description=parsedline[2],
                                           password=password)
                if pom.lower() == 'y' or pom == '':
                    grantroles(ks, projects, roles)
                printuser(parsedline[0], parsedline[1], parsedline[2], password)
            except Exception as e:
                print("Creation of user " + parsedline[0] + " failed: " + str(e))
else:
    print("Nothing passed to script. Use -h to print help.")







