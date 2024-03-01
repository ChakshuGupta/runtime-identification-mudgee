from src.objects.flow import Flow

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


    def set_from_profile(self, flow):
        """
        Generate flow from MUD profile
        """
        self.sip = flow.sip if flow.sip is not None else "*"
        self.dip = flow.dip if flow.dip is not None else "*"

        self.sport = flow.sport if flow.sport is not None else "*"
        self.dport = flow.dport if flow.dport is not None else "*"

        self.proto = flow.proto if flow.proto is not None else "*"

    def get_leaf(self):
        """
        Returns a tuple of all the fields of the flow
        """
        return (self.sip, self.dip, self.sport, self.dport, self.proto)
    
    def __eq__(self, __value: object) -> bool:
        """
        Override equality operator to match flows.
        """
        sip_eq = bool(self.sip == __value.sip)
        dip_eq = bool(self.dip == __value.dip)

        sport_eq = bool(self.sport == __value.sport)
        dport_eq = bool(self.dport == __value.dport)

        proto_eq = bool(self.proto == __value.proto)

        return (sip_eq and dip_eq and sport_eq and dport_eq and proto_eq)
