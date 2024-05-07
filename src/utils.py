import csv
import ipaddress
import json
import os
import re
import socket

from src.constants import IP_TYPES

def read_csv(filepath):
    """
    Reads the csv file and returns the contents of the file.

    [Args]
    filepath
    """
    content = []
    if os.path.splitext(filepath)[-1] == ".csv":
        with open(filepath) as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                content.append(row)
    else:
        print("ERROR! Expected .csv file but got ", os.path.splittext(filepath)[-1])
    return content


def read_json(filepath):
    """
    Reads json file and returns the contents of the file.

    [Args]
    filepath
    """
    content = {}
    if os.path.splitext(filepath)[-1] == ".json":
        with open(filepath) as json_file:
            content = json.load(json_file)
    else:
        print("ERROR! Expected .json file but got ", os.path.splittext(filepath)[-1])    
    return content


def is_valid_hostname(hostname):
    """
    from : https://stackoverflow.com/questions/2532053/validate-a-hostname-string
    """
    if len(hostname) > 255:
        return False
    if hostname[-1] == ".":
        hostname = hostname[:-1] # strip exactly one dot from the right, if present
    allowed = re.compile("(?!-)[A-Z\d-]{1,63}(?<!-)$", re.IGNORECASE)
    return all(allowed.match(x) for x in hostname.split("."))


def get_hostname(ip_address):
    """
    Returns the hostname using the IP address

    [Args]
    ip_address

    [Returns]
    host
    """
    if ip_address != "*":
        try:
            host = ipaddress.ip_address(ip_address).reverse_pointer
        except:
            try:
                res = socket.gethostbyaddr(ip_address)
                host = res[0]
            except:
                host = ip_address
    else:
        host = "*"
    
    return host

def get_ip_from_domain(domain):
    """
    Returns IP corresponding to the input domain

    [Args]
    domain

    [Returns]
    ip address
    """
    try:
        return socket.gethostbyname(domain)
    except:
        # if the corresponding IP does not exist, return the domain itself
        return domain


def get_ip_type(ip_address):
    """
    Identify the type of input in the profile (IPv4/IPv6/Domain/Subnet)

    [Args]
    ip_address

    [Returns]
    IP Type
    """
    try:
        if "/" not in ip_address:
            return IP_TYPES[1] if type(ipaddress.ip_address(ip_address)) is ipaddress.IPv4Address else IP_TYPES[2]
        else:
            return IP_TYPES[3]
    except ValueError:
        return IP_TYPES[0]
    

def is_ip_in_subnet(ip_address, subnet_address):
    """
    Check if the IP address is part of the given sub-network address

    [Args]
    ip_address
    subnet_address

    [Returns]
    True/False
    """
    network = ipaddress.ip_network(subnet_address)
    return ipaddress.ip_address(ip_address) in network