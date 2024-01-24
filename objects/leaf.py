class Leaf:
    def __init__(self, ethtype=None, proto=None, port=None):
        self.ethtype = ethtype
        self.proto = proto
        self.port = port
        self.port_type = None
    
    def set_ethtype(self, ethtype):
        self.ethtype = ethtype
    
    def get_ethtype(self):
        return self.ethtype
    
    def set_proto(self, proto):
        self.proto = proto

    def get_proto(self):
        return self.proto
    
    def set_port(self, port, port_type):
        self.port = port
        self.port_type = port_type

    def get_port(self):
        return self.port, self.port_type