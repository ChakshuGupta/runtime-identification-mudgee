from copy import deepcopy

from src.constants import IP_TYPES, PROTOCOLS
from src.objects.leaf import Leaf
from src.objects.node import Node
from src.objects.tree import Tree

from src.utils import get_ip_type,is_ip_in_subnet

def compute_similarity_scores(mud_profiles, runtime_profile):
    """
    Compute the similarity scores (as defined in the paper)

    [Args]
    mud_profiles: profile trees of all the MUD profiles
    runtime_profile: profile tree generated from the runtime network traffic

    [Returns]
    dynamic_scores: Ordered dictionary of the dynamic scores for all the devices
    static_scores: Ordered dictionary of the static scores for all the devices
    """
    dynamic_scores = {}
    static_scores = {}

    for device in mud_profiles:
        print("\n Checking device: ", device)
        # find the intersection between the MUD profile tree and the runtime profile tree
        intersection, temp_profile = find_intersection(mud_profiles[device], runtime_profile)

        print(runtime_profile.device_name, device, intersection)
        # compute the similarity scores
        dynamic_scores[device] = compute_dynamic_similarity(len(intersection), temp_profile.get_num_leaves())
        static_scores[device] = compute_static_similarity(len(intersection), mud_profiles[device].get_num_leaves())

    # Remove devices with 0 values for similarity scores
    dynamic_scores = {x:y for x,y in dynamic_scores.items() if (y is not None and y!=0) }
    static_scores = {x:y for x,y in static_scores.items() if (y is not None and y!=0) }
    
    # Sort the values according to the value
    dynamic_scores = sorted(dynamic_scores.items(), key=lambda item: item[1])
    static_scores = sorted(static_scores.items(), key=lambda item: item[1])

    return dynamic_scores, static_scores


def compute_dynamic_similarity(intersection_set_size, runtime_profile_set_size):
    """
    Computes the dynamic similarity score using the formula defined in the paper.

    [Args]
    matches: interection between the runtime profile and the mud profile
    runtime_profile

    [Returns]
    score: dynamic similarity score
    """
    score = 0

    # We use number of leaves as every path from the root to a leaf is considered a unique element
    # for the set. Hence, number of leaves gives us the number of elements in the set.
    score = intersection_set_size / runtime_profile_set_size

    # print("Dynamic score: ", score)

    return score


def compute_static_similarity(intersection_set_size, mud_profile_set_size):
    """
    Computes the static similarity score using the formula defined in the paper.

    [Args]
    matches: interection between the runtime profile and the mud profile
    mud_profile

    [Returns]
    score: static similarity score
    """
    score = 0
    
    score = intersection_set_size / mud_profile_set_size

    # print("Static score: ", score)
    
    return score


def find_intersection(mud_profile, runtime_profile):
    """
    Find overlapping sections between the two profiles and return the list of
    overlapping branches

    [Args]
    mud_profile: profile tree of the MUD profile
    runtime_profile: profile tree of the runtime profile
    """
    temp_runtime_profile = deepcopy(runtime_profile)
    intersection = []
    
    # Get the nodes from the runtime profile
    nodes = temp_runtime_profile.get_all_nodes()

    for node_name in nodes:
        # print("Checking node: ", node_name)
        # Check if the node exists in the MUD profile
        if mud_profile.get_node(node_name) == None:
            continue
        
        # Get all the edges (domains and leaves) from MUD profile and the runtime profile trees.
        mud_edges = mud_profile.get_node(node_name).get_edges()
        runtime_edges = nodes[node_name].get_edges()

        # Iterate through the edges from the runtime profile
        for runtime_domain in runtime_edges:
          
            # Iterate through all the edges of the MUD profile
            for mud_domain in mud_edges:
                # Get the leaves for the selected domain from the MUD profile
                mud_leaves = mud_profile.get_node(node_name).get_leaves(mud_domain)

                for mud_leaf in mud_leaves:
                    matches = []
                    # Get the type of IP info in the MUD profile (IPv4/IPv6/Domain/subnet)
                    mud_sip_type = get_ip_type(mud_leaf.sip)
                    mud_dip_type = get_ip_type(mud_leaf.dip)

                     # Get the leaves for the selected domain from the runtime profile
                    runtime_leaves = nodes[node_name].get_leaves(runtime_domain)

                    for runtime_leaf in runtime_leaves:

                         # Set the values in this tuple to False
                        (sip_match, dip_match, sport_match, dport_match, proto_match) = [False]*5

                        # compare the source IPs directly
                        if mud_leaf.sip == "*" or mud_leaf.sip == runtime_leaf.sip or mud_leaf.sdomain == runtime_leaf.sdomain:
                            sip_match = True
                        # if the MUD IP is a subnet, check if the runtime IP is in the subnet
                        elif mud_sip_type == IP_TYPES[3] and is_ip_in_subnet(runtime_leaf.sip, mud_leaf.sip):
                            sip_match = True
                        
                        # compare the destination IPs directly
                        if mud_leaf.dip == "*" or mud_leaf.dip == runtime_leaf.dip or mud_leaf.ddomain == runtime_leaf.ddomain:
                            dip_match = True
                        # if the MUD IP is a subnet, check if the runtime IP is in the subnet
                        elif mud_dip_type == IP_TYPES[3] and is_ip_in_subnet(runtime_leaf.dip, mud_leaf.dip):
                            dip_match = True
                        
                        # compare the src ports
                        if mud_leaf.sport == "*" or mud_leaf.sport == runtime_leaf.sport:
                            sport_match = True
                        
                        # compare the dst ports
                        if mud_leaf.dport == "*" or mud_leaf.dport == runtime_leaf.dport:
                            dport_match = True

                        # compare the protocols
                        if mud_leaf.proto == "*" or mud_leaf.proto == runtime_leaf.proto:
                            proto_match = True
                        
                        if PROTOCOLS.get(runtime_leaf.proto) == "UDP":
                             # if protocol is UDP, only check if src or dst port macthes and add to the matches list
                             if sip_match and dip_match and proto_match and (sport_match or dport_match) :
                                 matches.append((runtime_domain, runtime_leaf))
                        else:
                            # if all are true, add to the matches list
                            if sip_match and dip_match and sport_match and dport_match and proto_match:
                                matches.append((runtime_domain, runtime_leaf))
                    
                    # If matches exist, add to the intersection list
                    if len(matches) > 0:
                        intersection.append(matches[0])
                    if len(matches) > 1:
                        # If multiple leaves from the runtime match to the same MUD leaf, remove redundant leaves
                        # from the temporary runtime profile
                        print("\nRemove redundant leaves......")
                        # print(matches)
                        for iter in range(0, len(matches)-1):
                            temp_runtime_profile.get_node(node_name).remove_leaf(matches[iter+1][0], matches[iter+1][1])

    return intersection, temp_runtime_profile

