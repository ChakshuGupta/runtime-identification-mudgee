import os
import sys

from ipaddress import ip_address

from utils import read_csv, is_valid_hostname
from objects.edge import Edge
from objects.leaf import Leaf
from objects.node import Node
from objects.tree import Tree


def load_mud_profiles(model_dir):
    """
    Load the MUD profiles generated during the training phase.
    """
    mud_profiles = {}
    for root, dirs, files in os.walk(model_dir):
        if os.path.samefile(root, model_dir):
            continue
        device_name = os.path.basename(root)
        mud_profiles[device_name] = {}
        for file in files:
            # if "rule" in file:
            #     self.profiles[device_name]["rules"] = read_csv(os.path.join(root, file))
            if "ipflows" in file:
                mud_profiles[device_name]["flows"] = generate_mud_tree(
                                                                read_csv(
                                                                    os.path.join(root, file)
                                                                ),
                                                                device_name
                                                            )
            # elif "Mud" in file:
            #     self.profiles[device_name]["profile"] = read_json(os.path.join(root, file))
            else:
                continue


def generate_mud_tree(device_flows, device_name):
    mud_tree = Tree(device_name)
    for flow in device_flows:
        try:
            if flow["srcIp"]!= "*" and ip_address(flow["srcIp"]).is_private:
                node_name = "from LOCAL"
                node = mud_tree.get_node(node_name)
                if node is None:
                    node = Node("LOCAL", "from")       
                
                mud_tree.add_node(node)
            else:
                node_name = "from INTERNET"
                node = mud_tree.get_node(node_name)
                if node is None:
                    node = Node("INTERNET", "from")       
                
                mud_tree.add_node(node)

        except ValueError:
            if is_valid_hostname(flow["srcIp"]):
                node_name = "from INTERNET"
                node = mud_tree.get_node(node_name)
                if node is None:
                    node = Node("INTERNET", "from")       
                
                mud_tree.add_node(node)

        try:

            if flow["dstIp"]!= "*" and ip_address(flow["dstIp"]).is_private:
                node_name = "to LOCAL"
                node = mud_tree.get_node(node_name)
                if node is None:
                    node = Node("LOCAL", "to")    
                
                mud_tree.add_node(node)
            else:
                node_name = "to INTERNET"
                node = mud_tree.get_node(node_name)
                if node is None:
                    node = Node("INTERNET", "to")    
                
                mud_tree.add_node(node)

        except ValueError:
            if is_valid_hostname(flow["dstIp"]):
                node_name = "to INTERNET"
                node = mud_tree.get_node(node_name)
                if node is None:
                    node = Node("INTERNET", "to")       
                
                mud_tree.add_node(node)
            
        leaf = Leaf()
    return


if __name__ == "__main__":
    model_dir = sys.argv[1]
    load_mud_profiles(model_dir)