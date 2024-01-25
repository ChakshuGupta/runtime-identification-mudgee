import csv
import json
import os
import re
import socket


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


def get_domain(ip):
    if ip != "*":
        try:
            res = socket.gethostbyaddr(ip)
            domain = res[0]
        except:
            domain = ip
    else:
        domain = "*"
    
    return domain