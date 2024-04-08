import json

from src.objects.packet import Packet

class Flow(object):

    def __init__(self):
        """
        Initialise an empty packet
        """
        # intiialise src and dest IPs
        self.sip = None
        self.dip = None
        # initialise domain values for the ips
        self.sdomain = None
        self.ddomain = None
        # initialise src and dest ports
        self.sport = None
        self.dport = None
        # initialise protocol and ethType
        self.proto = None
        self.eth_type = None

        self.packets = list()

    def print(self):
        """
        """
        data = {
            'sip' : self.sip,
            'dip' : self.dip,
            "sdomain" : self.sdomain,
            "ddomain" : self.ddomain,
            'sport' : self.sport,
            'dport' : self.dport,
            'ip_proto' : self.proto,
            'eth_type': self.eth_type
        }
        print(json.dumps(data, indent=4))

    def add(self, pkt):
        """
        Add a packet to the flow using IPs and Port numbers
        """

        if self.sip is not None:
            if {self.sip, self.dip} != {pkt.sip, pkt.dip} and\
                  {self.sport, self.dport} != {pkt.sport, pkt.dport}:
                return
        # Set endpoints for the flow            
        elif pkt.sport > pkt.dport:
            self.sip = pkt.sip
            self.dip = pkt.dip

            self.sport = pkt.sport
            self.dport = pkt.dport
        
        else:
            self.sip = pkt.dip
            self.dip = pkt.sip

            self.sport = pkt.dport
            self.dport = pkt.sport

        self.proto = pkt.proto
        self.eth_type = int(pkt.eth_type, 16)

        # Add packet to the flow
        self.packets.append(pkt)

        return self
    
    def set_domain(self, ip, domain):
        """
        Set the domains for the flow ips
        """
        if ip == self.sip:
            self.sdomain = domain
        elif ip == self.dip:
            self.ddomain = domain
