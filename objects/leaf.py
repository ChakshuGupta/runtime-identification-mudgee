import json

from objects.flow import Flow
class Leaf(Flow):
    def __init__(self):
        """
        Leaf node of the profile tree consists of the ip flow information
        """
        # intiialise src and dest IPs
        self.sip = None
        self.dip = None
        # initialise src and dest ports
        self.sport = None
        self.dport = None
        # initialise protocol
        self.proto = None
        self.eth_type = None

    def set_from_profile(self, flow):
        """
        Generate flow from MUD profile
        """
        self.sip = flow.sip
        self.dip = flow.dip

        self.sport = flow.sport
        self.dport = flow.dport

        self.proto = flow.proto
        self.eth_type = flow.eth_type
        
        return self

    def get_leaf(self):
        """
        Returns a tuple of all the fields of the flow
        """
        return (self.sip, self.dip, self.sport, self.dport, self.proto, self.eth_type)