from ipaddress import ip_address

from src.constants import *
from src.utils import get_hostname, get_ip_type, get_ip_from_domain
from src.objects.flow import Flow
from src.objects.leaf import Leaf
from src.objects.node import Node
from src.objects.tree import Tree 


def add_to_node(comp, dir, profile_tree, flow, type):
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
        if type == "runtime":
            if new_leaf.dip == profile_tree.default_gateway:
                if new_leaf.dport == DNS_PORT:
                    new_leaf.ddomain = DNS_CONTROLLER
                elif new_leaf.dport == NTP_PORT:
                    new_leaf.ddomain = NTP_CONTROLLER
                else:
                    new_leaf.ddomain = DEFAULTGATEWAYCONTROLLER
        domain = new_leaf.ddomain

    elif dir == "from":
        if type == "runtime":
            if new_leaf.sip == profile_tree.default_gateway:
                if new_leaf.sport == DNS_PORT:
                    new_leaf.sdomain = DNS_CONTROLLER
                elif new_leaf.sport == NTP_PORT:
                    new_leaf.sdomain = NTP_CONTROLLER
                else:
                    new_leaf.sdomain = DEFAULTGATEWAYCONTROLLER

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



# def update_node(comp, dir, profile_tree, flow):
#     """
#     Update the node in the tree. This adds a new node or adds edges and/or leaves
#     to existing nodes.

#     [Args]
#     comp: the component (local/internet) involved in the flow
#     dir: the direction of the communication (to/from)
#     profile_tree: tree object of the runtime profile of the device getting generated
#     flow: the current flow getting processed to add to the node (if not there)
#     """
#     node_name = dir + " " + comp
#     node = profile_tree.get_node(node_name)
#     if node is None:
#         add_to_node(comp, dir, profile_tree, flow, "runtime")
#         return

#     new_leaf = Leaf()
#     new_leaf.set_from_profile(flow)

#     if dir == "to":
#         if new_leaf.dip == profile_tree.default_gateway:
#             if new_leaf.dport == DNS_PORT:
#                 new_leaf.ddomain = DNS_CONTROLLER
#             elif new_leaf.dport == NTP_PORT:
#                 new_leaf.ddomain = NTP_CONTROLLER
#             else:
#                 new_leaf.ddomain = DEFAULTGATEWAYCONTROLLER
        
#         domain = new_leaf.ddomain
#         leaves = node.get_leaves(new_leaf.ddomain)

#     elif dir == "from":
#         if new_leaf.sip == profile_tree.default_gateway:
#             if new_leaf.sport == DNS_PORT:
#                 new_leaf.sdomain = DNS_CONTROLLER
#             elif new_leaf.sport == NTP_PORT:
#                 new_leaf.sdomain = NTP_CONTROLLER
#             else:
#                 new_leaf.sdomain = DEFAULTGATEWAYCONTROLLER

#         domain = new_leaf.sdomain
#         leaves = node.get_leaves(new_leaf.sdomain)
    
#     else: # Probably not needed. Just to cover all cases
#         return ValueError

#     if leaves is None:
#         print("----------- Add new leaf to the tree ------------")
#         node.add_leaf(new_leaf, domain)
#     else:
#         match_found = False
#         # compare the leaves to find a match
#         for leaf in leaves:
#             if leaf == new_leaf:
#                 match_found = True
        
#         if not match_found:
#             node.add_leaf(new_leaf, domain)
    
#     return


def update_runtime_profile(flows, profile_tree):
    """
    Update the runtime profile tree at every epoch with the new flows.

    [Args]
    flows: List of recorded IP flows
    profile_tree: tree object of the runtime profile of the device
    """
    # if profile_tree.is_empty():
    # generate the initial tree
    for flow_key in flows:
        if ip_address(flows[flow_key].sip).is_private:
            comp = "Local"
            dir = "from"
        else:
            comp = "Internet"
            dir = "from"
        add_to_node(comp, dir, profile_tree, flows[flow_key], "runtime")

        if ip_address(flows[flow_key].dip).is_private:
            comp = "Local"
            dir = "to"
        else:
            comp = "Internet"
            dir = "to"
        add_to_node(comp, dir, profile_tree, flows[flow_key], "runtime")
        # print("Number of leaves: " + str(profile_tree.get_num_leaves()))
        
    # else:
        # for flow_key in flows:
        #     if ip_address(flows[flow_key].sip).is_private:
        #         comp = "Local"
        #         dir = "from"
        #     else:
        #         comp = "Internet"
        #         dir = "from"
        #     update_node(comp, dir, profile_tree, flows[flow_key])

        #     if ip_address(flows[flow_key].dip).is_private:
        #         comp = "Local"
        #         dir = "to"
        #     else:
        #         comp = "Internet"
        #         dir = "to"
        #     update_node(comp, dir, profile_tree, flows[flow_key])
        # print("Number of leaves: " + str(profile_tree.get_num_leaves()))


def add_ace_to_flow(flow_local, flow_internet, ace_matches):
    """
    Add the access control list to the flow
    """
    for match_key in ace_matches.keys():
        if "ipv" in match_key:
            net_keys = ace_matches[match_key].keys()

            for key in net_keys:
                if "source" in key:
                    flow_local.sip = ace_matches[match_key][key]
                    flow_internet.sip = ace_matches[match_key][key]
                elif "destination" in key:
                    flow_local.dip = ace_matches[match_key][key]
                    flow_internet.dip = ace_matches[match_key][key]
                elif key == "ietf-acldns:dst-dnsname":
                    flow_local.dip = ace_matches[match_key][key]
                    flow_internet.dip = ace_matches[match_key][key]
                    flow_local.ddomain = ace_matches[match_key][key]
                    flow_internet.ddomain = ace_matches[match_key][key]
                elif key == "ietf-acldns:src-dnsname":
                    flow_local.sip = ace_matches[match_key][key]
                    flow_internet.sip = ace_matches[match_key][key]
                    flow_local.sdomain = ace_matches[match_key][key]
                    flow_internet.sdomain = ace_matches[match_key][key]
                elif key == "protocol":
                    flow_local.proto = ace_matches[match_key][key]
                    flow_internet.proto = ace_matches[match_key][key]
        
        elif match_key == "ietf-mud:mud" and "controller" in ace_matches[match_key]:
            flow_local.sip = ace_matches[match_key]["controller"]
            flow_local.sdomain = ace_matches[match_key]["controller"]

        elif match_key == "tcp":
            if "destination-port" in ace_matches[match_key]:
                flow_local.dport = ace_matches[match_key]["destination-port"]["port"]
                flow_internet.dport = ace_matches[match_key]["destination-port"]["port"]
            elif "source-port" in ace_matches[match_key]:
                flow_local.sport = ace_matches[match_key]["source-port"]["port"]
                flow_internet.sport = ace_matches[match_key]["source-port"]["port"]
        
        elif match_key == "udp":
            if "destination-port" in ace_matches[match_key]:
                flow_local.dport = ace_matches[match_key]["destination-port"]["port"]
                flow_internet.dport = ace_matches[match_key]["destination-port"]["port"]
            elif "source-port" in ace_matches[match_key]:
                flow_local.sport = ace_matches[match_key]["source-port"]["port"]
                flow_internet.sport = ace_matches[match_key]["source-port"]["port"]
        
        elif match_key == "eth":
            flow_local.eth_type = int(ace_matches[match_key]["ethertype"], 16)
            flow_internet.eth_type = int(ace_matches[match_key]["ethertype"], 16)


def generate_mud_profile_tree(mud_profile):
    """
    Generate the tree structure using the MUD profiles.

    [Args]:
    mud_profile: MUD profile of the device read in the JSON format

    [Returns]:
    mud_profile_tree
    """
    # Generate new tree object
    # systeminfo == device name
    mud_profile_tree = Tree(mud_profile["ietf-mud:mud"]["systeminfo"])

    # [Deprecated]
    # # Get access lists
    # from_device_policy = mud_profile["ietf-mud:mud"]["from-device-policy"]["access-lists"]["access-list"]
    # to_device_policy = mud_profile["ietf-mud:mud"]["to-device-policy"]["access-lists"]["access-list"]

    # # Get names of the to and from device policy names
    # from_device_name = from_device_policy[0]["name"] if len(from_device_policy) > 0 else None
    # to_device_name = to_device_policy[0]["name"] if len(to_device_policy) > 0 else None
    
    # Get the Access Control List from the MUD profile
    access_control_list = mud_profile["ietf-access-control-list:access-lists"]["acl"]

    for acl in access_control_list:
        aces = acl["aces"]["ace"]
        # Get the list of ACEs
        for ace in aces:
            flow_local = Flow()
            flow_internet = Flow()
            matches = ace["matches"]
            # if the acl is for "to-device" policy, it is also "from-internet"
            if "to" in acl["name"]:
                
                add_ace_to_flow(flow_local, flow_internet, matches)
                
                if flow_local.sip is not None:
                    if flow_local.sdomain is None:
                        flow_local.sdomain = get_hostname(flow_local.sip)
                    elif get_ip_type(flow_local.sip) == IP_TYPES[0]:
                        flow_local.sdomain, flow_local.sip = get_ip_from_domain(flow_local.sdomain)
                    add_to_node("Local", "to", mud_profile_tree, flow_local, "mud")
                
                if flow_internet.sip is not None:
                    if flow_internet.sdomain is None:
                        flow_internet.sdomain = get_hostname(flow_internet.sip)
                    elif get_ip_type(flow_internet.sip) == IP_TYPES[0]:
                        flow_internet.sdomain, flow_internet.sip = get_ip_from_domain(flow_internet.sdomain)
                    add_to_node("Internet", "from", mud_profile_tree, flow_internet, "mud")
                

           # if the acl is for "from-device", it is also "to-internet"
            elif "from" in acl["name"]:
                
                add_ace_to_flow(flow_local, flow_internet, matches)
                
                if flow_local.dip is not None:
                    if flow_local.ddomain is None:
                        flow_local.ddomain = get_hostname(flow_local.dip)
                    elif get_ip_type(flow_local.dip) == IP_TYPES[0]:
                        flow_local.ddomain, flow_local.dip = get_ip_from_domain(flow_local.ddomain)
                    add_to_node("Local", "from", mud_profile_tree, flow_local, "mud")
            
                if flow_internet.dip is not None:
                    if flow_internet.ddomain is None:
                        flow_internet.ddomain = get_hostname(flow_internet.dip)
                    elif get_ip_type(flow_internet.dip) == IP_TYPES[0]:
                        flow_internet.ddomain, flow_internet.dip = get_ip_from_domain(flow_internet.ddomain)
                    add_to_node("Internet", "to", mud_profile_tree, flow_internet, "mud")

            else:
                print("ERROR! Unknown policy type: ", acl["name"])
            
    mud_profile_tree.print()

    return mud_profile_tree