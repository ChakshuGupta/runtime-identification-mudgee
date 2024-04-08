from src.objects.flow import Flow
from src.utils import get_hostname

class Leaf(Flow):
    def __init__(self):
        """
        Leaf node of the profile tree consists of the ip flow information
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
        # initialise protocol
        self.proto = None
        self.eth_type = None

    def set_from_profile(self, flow):
        """
        Generate flow from MUD profile
        """
        self.sip = flow.sip if flow.sip is not None else "*"
        self.dip = flow.dip if flow.dip is not None else "*"

        self.sport = flow.sport if flow.sport is not None else "*"
        self.dport = flow.dport if flow.dport is not None else "*"

        self.proto = flow.proto if flow.proto is not None else "*"
        self.eth_type = flow.eth_type if flow.eth_type is not None else "*"

        # initialise domain values for the ips
        self.sdomain = flow.sdomain if flow.sdomain is not None else get_hostname(flow.sip)
        self.ddomain = flow.ddomain if flow.ddomain is not None else get_hostname(flow.dip)

    def get_leaf(self):
        """
        Returns a tuple of all the fields of the flow
        """
        return (self.sip, self.dip, self.sport, self.dport, self.proto)
    
    def __eq__(self, other: object) -> bool:
        """
        Override equality operator to match flows.
        """
        if isinstance(other, Leaf):

            sip_eq = bool(self.sip == other.sip) or bool(self.sdomain == other.sdomain)
            dip_eq = bool(self.dip == other.dip) or bool(self.ddomain == other.ddomain)

            sport_eq = bool(self.sport == other.sport)
            dport_eq = bool(self.dport == other.dport)

            proto_eq = bool(self.proto == other.proto)

            return (sip_eq and dip_eq and sport_eq and dport_eq and proto_eq)

        else:
            return False
