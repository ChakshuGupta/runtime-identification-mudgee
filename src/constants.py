
DEFAULTGATEWAYCONTROLLER = "urn:ietf:params:mud:gateway"
NTP_CONTROLLER = "urn:ietf:params:mud:ntp"
DNS_CONTROLLER = "urn:ietf:params:mud:dns"

DNS_PORT = "53"
NTP_PORT = "123"

IP_TYPES = {
    0: "Domain",
    1: "IPv4",
    2: "IPv6",
    3: "Subnet"
}

PROTOCOLS = {
    6  : 'TCP',
    17 : 'UDP'
}

EPOCH_TIME = 900000  # = 15 minutes