import json
class Leaf:
    def __init__(self):
        """
        Leaf node of the profile tree consists of the ip flow information
        """
        self.ethtype = None
        # intiialise src and dest IPs
        self.sip = None
        self.dip = None
        # initialise src and dest ports
        self.sport = None
        self.dport = None
        # initialise protocol
        self.proto = None
    
    def print(self):
        """
        Print the flow information
        """
        data = {
            'sip' : self.sip,
            'dip' : self.dip,
            'sport' : self.sport,
            'dport' : self.dport,
            'ip_proto' : self.proto,
            'ethType': self.ethtype
        }
        print(json.dumps(data, indent=4))


    def set_from_profile(self, flow):
        """
        Generate flow from MUD profile
        """
        self.sip = flow["srcIp"]
        self.dip = flow["dstIp"]

        self.sport = flow["srcPort"]
        self.dport = flow["dstPort"]

        self.proto = flow["ipProto"]
        self.ethtype = int(flow["ethType"], 16)
        
        return self

    def get_flow(self):
        """
        Returns a tuple of all the fields of the flow
        """
        return (self.sip, self.dip, self.sport, self.dport, self.proto, self.ethtype)