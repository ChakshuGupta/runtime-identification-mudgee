import os
import sys

from ipaddress import ip_address

from utils import read_csv, is_valid_hostname, get_domain
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


def add_to_node(comp, dir, mud_tree, flow):
    node_name = dir + " " + comp
    node = mud_tree.get_node(node_name)
    if node is None:
        node = Node(comp, dir)

    leaf = Leaf()
    leaf = leaf.set_from_profile(flow)

    if comp == "Local" and dir == "to":
        domain = get_domain(flow["dstIp"])
        node.add_leaf(leaf, domain)
    elif comp == "Local" and dir == "from":
        domain = get_domain(flow["srcIp"])
        node.add_leaf(leaf, domain)
    elif comp == "Internet" and dir == "to":
        domain = get_domain(flow["dstIp"])
        node.add_leaf(leaf, domain)
    elif comp == "Internet" and dir == "from":
        domain = get_domain(flow["srcIp"])
        node.add_leaf(leaf, domain)

    mud_tree.add_node(node)


def generate_mud_tree(device_flows, device_name):
    mud_tree = Tree(device_name)
    for flow in device_flows:
        try:
            if flow["srcIp"]!= "*" and ip_address(flow["srcIp"]).is_private:
                comp = "Local"
                dir = "from"
                
            else:
                comp = "Internet"
                dir = "from"
            
            add_to_node(comp, dir, mud_tree, flow)

        except ValueError:
            if is_valid_hostname(flow["srcIp"]):
                comp = "Internet"
                dir = "from"
                add_to_node(comp, dir, mud_tree, flow)

        try:

            if flow["dstIp"]!= "*" and ip_address(flow["dstIp"]).is_private:
                comp = "Local"
                dir = "to"

            else:
                comp = "Internet"
                dir = "to"
            
            add_to_node(comp, dir, mud_tree, flow)

        except ValueError:
            if is_valid_hostname(flow["dstIp"]):
                comp = "Internet"
                dir = "to"
                add_to_node(comp, dir, mud_tree, flow)
            
        leaf = Leaf()
    
    print(mud_tree.get_all_nodes())
    return mud_tree


if __name__ == "__main__":
    model_dir = sys.argv[1]
    load_mud_profiles(model_dir)