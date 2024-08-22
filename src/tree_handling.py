from ipaddress import ip_address

from src.constants import *
from src.utils import get_hostname, get_ip_type, get_ip_from_domain
from src.objects.flow import Flow
from src.objects.leaf import Leaf
from src.objects.node import Node
from src.objects.tree import Tree 


def add_to_node(comp, dir, profile_tree, flow):
    """
    Add flow to the tree. This adds a new node or adds edges and/or leaves
    to existing nodes.

    [Args]
    comp: the component (local/internet) involved in the flow
    dir: the direction of the communication (to/from)
    profile_tree: tree object of the profile of the device getting generated (MUD/runtime)
    flow: the flow that needs to be added to the node
    """
    node_name = dir + " " + comp
    node = profile_tree.get_node(node_name)
    if node is None:
        new_node = True
        node = Node(comp, dir)
    else:
        new_node = False

    new_leaf = Leaf()
    new_leaf.set_from_profile(flow)

    if dir == "to":
        domain = new_leaf.ddomain

    elif dir == "from":
        domain = new_leaf.sdomain
    
    leaves = node.get_leaves(domain)
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
    
    if new_node:
        profile_tree.add_node(node)
    
    return


def update_runtime_profile(flows, profile_tree):
    """
    Update the runtime profile tree at every epoch with the new flows.

    [Args]
    flows: List of recorded IP flows
    profile_tree: tree object of the runtime profile of the device
    """
    for flow_key in flows:

        if ip_address(flows[flow_key].sip).is_private and ip_address(flows[flow_key].dip).is_private:
            if flows[flow_key].dip == profile_tree.default_gateway:
                if flows[flow_key].dport == DNS_PORT:
                    flows[flow_key].ddomain = DNS_CONTROLLER
                elif flows[flow_key].dport == NTP_PORT:
                    flows[flow_key].ddomain = NTP_CONTROLLER
                else:
                    flows[flow_key].ddomain = DEFAULTGATEWAYCONTROLLER
                comp = "Local"
                dir = "from"
            
            else:
                comp = "Local"
                dir = "to"


        elif ip_address(flows[flow_key].sip).is_private:
            comp = "Internet"
            dir = "to"

        elif ip_address(flows[flow_key].dip).is_private:
            comp = "Internet"
            dir = "from"
        
        else:
            print(flows[flow_key].sip, flows[flow_key].dip)
            continue

        add_to_node(comp, dir, profile_tree, flows[flow_key])



def add_ace_to_flow(flow, ace_match):
    """
    Add the access control list to the flow
    """
    is_local = False
    for match_key in ace_match.keys():
        if "ipv" in match_key:
            net_keys = ace_match[match_key].keys()

            for key in net_keys:
                if "source" in key:
                    flow.sip = ace_match[match_key][key]
                    if ip_address(flow.sip.split("/")[0]).is_private:
                        is_local = True
                elif "destination" in key:
                    flow.dip = ace_match[match_key][key]
                    if ip_address(flow.dip.split("/")[0]).is_private:
                        is_local = True
                elif key == "ietf-acldns:dst-dnsname":
                    flow.dip = ace_match[match_key][key]
                    flow.ddomain = ace_match[match_key][key]
                elif key == "ietf-acldns:src-dnsname":
                    flow.sip = ace_match[match_key][key]
                    flow.sdomain = ace_match[match_key][key]
                elif key == "protocol":
                    flow.proto = ace_match[match_key][key]
        
        elif match_key == "ietf-mud:mud" and "controller" in ace_match[match_key]:
            flow.sip = ace_match[match_key]["controller"]
            flow.sdomain = ace_match[match_key]["controller"]
            is_local = True

        elif match_key == "tcp":
            if "destination-port" in ace_match[match_key]:
                flow.dport = ace_match[match_key]["destination-port"]["port"]
            elif "source-port" in ace_match[match_key]:
                flow.sport = ace_match[match_key]["source-port"]["port"]
        
        elif match_key == "udp":
            if "destination-port" in ace_match[match_key]:
                flow.dport = ace_match[match_key]["destination-port"]["port"]

            elif "source-port" in ace_match[match_key]:
                flow.sport = ace_match[match_key]["source-port"]["port"]
        
        elif match_key == "eth":
            flow.eth_type = int(ace_match[match_key]["ethertype"], 16)
    
    return is_local


def generate_mud_profile_tree(mud_profile):
    """
    Generate the tree structure using the MUD profiles.

    [Args]:
    mud_profile: MUD profile of the device read in the JSON format

    [Returns]:
    mud_profile_tree
    """
    # Generate the tree object for the MUD profile
    # systeminfo gives us the device name
    mud_profile_tree = Tree(mud_profile["ietf-mud:mud"]["systeminfo"])

   
    # Get the Access Control List from the MUD profile
    access_control_list = mud_profile["ietf-access-control-list:access-lists"]["acl"]

    for acl in access_control_list:
        aces = acl["aces"]["ace"]
        # Get the list of ACEs
        for ace in aces:
            flow = Flow()
            matches = ace["matches"]
            # if the acl is for "to-device" policy
            if "to" in acl["name"]:
                
                is_local = add_ace_to_flow(flow, matches)
                
                if flow.sip is not None:
                    if flow.sdomain is None:
                        flow.sdomain = get_hostname(flow.sip)
                    elif get_ip_type(flow.sip) == IP_TYPES[0]:
                        flow.sdomain, flow.sip = get_ip_from_domain(flow.sdomain)
                        if get_ip_type(flow.sip) != IP_TYPES[0]:
                            is_local = ip_address(flow.sip).is_private
                    if is_local:
                        add_to_node("Local", "from", mud_profile_tree, flow)
                    else:
                        add_to_node("Internet", "from", mud_profile_tree, flow)
                                

           # if the acl is for "from-device"
            elif "from" in acl["name"]:
                
                is_local = add_ace_to_flow(flow, matches)
                
                if flow.dip is not None:
                    if flow.ddomain is None:
                        flow.ddomain = get_hostname(flow.dip)
                    elif get_ip_type(flow.dip) == IP_TYPES[0]:
                        flow.ddomain, flow.dip = get_ip_from_domain(flow.ddomain)
                        if get_ip_type(flow.dip) != IP_TYPES[0]:
                            is_local = ip_address(flow.dip).is_private
                    if is_local:
                        add_to_node("Local", "to", mud_profile_tree, flow)
                    else:
                        add_to_node("Internet", "to", mud_profile_tree, flow)

            else:
                print("ERROR! Unknown policy type: ", acl["name"])
            
    mud_profile_tree.print()

    return mud_profile_tree