# Create OpenStack user by OpenStack client with automaticaly generated password
# Lukas Stehlik 2017
#
# usage:
#       create-user <username> <e-mail>
#
# output:
#       OpenStack client output
#       +
#       User password: <random-password>
#
#

arg1=$1
arg2=$2


if [[ -n "$arg1" ]] && ([ $arg1 == "help" ] || [ $arg1 == "-h" ] || [ $arg1 == "--help" ]); then
    echo "usage:"
    echo "create-user <username> <e-mail>"
    echo "arguments:"
    echo -e "\t<username>\t- Name (login) of new user"
    echo -e "\t<e-mail>\t- E-mail of new user (optional)\n"
    exit 1
fi

random=$(< /dev/urandom tr -dc [:alnum:] | head -c12)

if [[ -n "$arg1" ]] && [[ -n "$arg2" ]]; then
    output=$(openstack user create  --password $random  --email $arg2 $arg1)
    echo $output
    echo "User password: $random"
elif [[ -n "$arg1" ]]; then
    output=$(openstack user create  --password $random $arg1)
    echo $output
    echo "User password: $random"
else
    echo "Wrong arguments were passed"
fi
