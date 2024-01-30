import os
import sys
import yaml

from ipaddress import ip_address

from read_pcap import *
from utils import read_csv, is_valid_hostname, get_domain
from objects.flow import Flow
from objects.leaf import Leaf
from objects.node import Node
from objects.tree import Tree
    

def add_to_node(comp, dir, mud_tree, flow):
    """
    Add flow to the tree. This adds a new node or adds edges and/or leaves
    to existing nodes.
    """
    node_name = dir + " " + comp
    node = mud_tree.get_node(node_name)
    if node is None:
        node = Node(comp, dir)

    leaf = Leaf()
    leaf.set_from_profile(flow)

    if dir == "to":
        domain = get_domain(flow.dip)
        node.add_leaf(leaf, domain)
    elif dir == "from":
        domain = get_domain(flow.sip)
        node.add_leaf(leaf, domain)

    mud_tree.add_node(node)


def update_node(comp, dir, mud_tree, flow):
    """
    Update the node in the tree. This adds a new node or adds edges and/or leaves
    to existing nodes.
    """
    node_name = dir + " " + comp
    node = mud_tree.get_node(node_name)
    if node is None:
        add_to_node(comp, dir, mud_tree, flow)

    if dir == "to":
        domain = get_domain(flow.dip)
        leaves = node.get_leaves(domain)

    elif dir == "from":
        domain = get_domain(flow.sip)
        leaves = node.get_leaves(domain)
    
    else: # Probably not needed. Just to cover all cases
        return ValueError

    new_leaf = Leaf()
    new_leaf.set_from_profile(flow)

    if leaves is None:
        print("----------- Add new leaf to the tree ------------")
        node.add_leaf(new_leaf, domain)
    else:
        match_found = False
        # compare the leaves to find a match
        for leaf in leaves:
            if leaf == new_leaf:
                match_found = True
        
        if not match_found:
            node.add_leaf(new_leaf, domain)
                


def generate_mud_tree(device_flows, device_name):
    """
    Generates the profile tree from the existing MUD profiles
    """
    mud_tree = Tree(device_name)
    for flow in device_flows:
        try:
            if flow.sip != "*" and ip_address(flow.sip).is_private:
                comp = "Local"
                dir = "from"
                add_to_node(comp, dir, mud_tree, flow)
                
            elif flow.sip!= "*":
            # else:
                comp = "Internet"
                dir = "from"
                add_to_node(comp, dir, mud_tree, flow)

        except ValueError:
            if is_valid_hostname(flow.sip):
                comp = "Internet"
                dir = "from"
                add_to_node(comp, dir, mud_tree, flow)

        try:

            if flow.dip!= "*" and ip_address(flow.dip).is_private:
                comp = "Local"
                dir = "to"
                add_to_node(comp, dir, mud_tree, flow)

            elif flow.dip!= "*":
            # else:
                comp = "Internet"
                dir = "to"
                add_to_node(comp, dir, mud_tree, flow)
            
            
        except ValueError:
            if is_valid_hostname(flow.dip):
                comp = "Internet"
                dir = "to"
                add_to_node(comp, dir, mud_tree, flow)
                
    # print(mud_tree.get_all_nodes())
    mud_tree.print()
    return mud_tree


def generate_flows_from_profile(flows_json):
    """
    """
    flows = []
    for flow in flows_json:
        flows.append(Flow().from_profile(flow))
    return flows


def load_mud_profiles(model_dir):
    """
    Load the MUD profiles generated during the training phase.
    """
    mud_profiles = dict()
    for root, dirs, files in os.walk(model_dir):
        if os.path.samefile(root, model_dir):
            continue
        device_name = os.path.basename(root)
        mud_profiles[device_name] = dict()
        for file in files:
            # if "rule" in file:
            #     self.profiles[device_name]["rules"] = read_csv(os.path.join(root, file))
            if "ipflows" in file:
                flows = generate_flows_from_profile(
                            read_csv(
                                os.path.join(root, file)
                                )
                            )
                mud_profiles[device_name] = generate_mud_tree( flows, device_name)
            # elif "Mud" in file:
            #     self.profiles[device_name]["profile"] = read_json(os.path.join(root, file))
            else:
                continue
    return mud_profiles


def compute_similarity_scores(mud_profiles):
    pass


def update_runtime_profile(flows, profile_tree):
    if profile_tree.is_empty():
        # generate the initial tree
        for flow in flows:
            print(flows[flow].sip, flows[flow].dip)
            if ip_address(flows[flow].sip).is_private:
                comp = "Local"
                dir = "from"
            else:
                comp = "Internet"
                dir = "from"
            add_to_node(comp, dir, profile_tree, flows[flow])

            if ip_address(flows[flow].dip).is_private:
                comp = "Local"
                dir = "to"
            else:
                comp = "Internet"
                dir = "to"
            add_to_node(comp, dir, profile_tree, flows[flow])
        
        profile_tree.print()
    else:
        for flow in flows:
            print(flows[flow].sip, flows[flow].dip)
            if ip_address(flows[flow].sip).is_private:
                comp = "Local"
                dir = "from"
            else:
                comp = "Internet"
                dir = "from"
            update_node(comp, dir, profile_tree, flows[flow])

            if ip_address(flows[flow].dip).is_private:
                comp = "Local"
                dir = "to"
            else:
                comp = "Internet"
                dir = "to"
            update_node(comp, dir, profile_tree, flows[flow])
        
        profile_tree.print()


def runtime_profile_generation(input_dir, mud_profiles, device_name):
    """
    Generate the runtime profile from the input packets
    """
    pcap_list = get_pcaps_from_dir(input_dir)
    
    if len(pcap_list) == 0:
        return None
    
    packets = list()
    for pcap in pcap_list:
        packets.extend(read_pcap(pcap))
    
    # Order read packets using time
    packets  = sorted(packets, key=lambda ts: ts.time)

    start_time = packets[0].time # time of the first packet
    end_time = packets[-1].time # time of the last packet
    epoch_time = 900000 # = 15 minutes
    in_time = 0 # time passed since the beginning of the epoch

    # print the duration of the packet capture
    print("\n\n------- Total time: " + str(end_time - start_time) + " -------\n\n")

    flows = dict()
    profile_tree = Tree(device_name)
    # Traverse the packets in the list
    for packet in packets:
        # Check if packet has none fields
        if packet.is_none():
            continue
        in_time = packet.time - start_time
        if in_time > epoch_time:
            in_time = 0
            start_time = start_time + epoch_time
            update_runtime_profile(flows, profile_tree)

            compute_similarity_scores(mud_profiles)

        # Generate a key using packet protocol and a frozen set of source IP and destination IP
        # Using frozenset to ensure the key is hashable (a requirement for dict keys)
        key = (packet.proto, frozenset({packet.sip, packet.dip}))
        # Add a the packet to the flow
        flows[key] = flows.get(key, Flow()).add(packet)

    return flows



if __name__ == "__main__":
    config = sys.argv[1]
    with open(config, 'r') as cfgfile:
        cfg = yaml.load(cfgfile, Loader=yaml.Loader)

    mud_profiles = load_mud_profiles(cfg["dir-mud-profiles"])

    runtime_profile_generation(cfg["dir-pcaps"], mud_profiles, cfg["device-name"])