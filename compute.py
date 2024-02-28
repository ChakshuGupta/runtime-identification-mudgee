from constants import IP_TYPES
from objects.leaf import Leaf
from objects.node import Node
from objects.tree import Tree

from utils import get_ip_type, get_hostname, get_ip_from_domain, is_ip_in_subnet

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
        matches = find_intersection(mud_profiles[device], runtime_profile)

        # compute the similarity scores
        dynamic_scores[device] = compute_dynamic_similarity(matches, runtime_profile)
        static_scores[device] = compute_static_similarity(matches, mud_profiles[device])
    
    dynamic_scores = sorted(dynamic_scores.items(), key=lambda item: item[1])
    static_scores = sorted(static_scores.items(), key=lambda item: item[1])

    return dynamic_scores, static_scores


def compute_dynamic_similarity(matches, runtime_profile):
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
    num_leaves = runtime_profile.get_num_leaves()
    score = len(matches) / num_leaves

    # print("Dynamic score: ", score)

    return score


def compute_static_similarity(matches, mud_profile):
    """
    Computes the static similarity score using the formula defined in the paper.

    [Args]
    matches: interection between the runtime profile and the mud profile
    mud_profile

    [Returns]
    score: static similarity score
    """
    score = 0

    num_leaves = mud_profile.get_num_leaves()
    score = len(matches) / num_leaves

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
    matches = []
    
    # Get the nodes from the runtime profile
    nodes = runtime_profile.get_all_nodes()

    for node in nodes:
        # Check if the node exists in the MUD profile
        if mud_profile.get_node(node) == None:
            continue
        
        # Get all the edges (domains and leaves) from MUD profile and the runtime profile trees.
        mud_edges = mud_profile.get_node(node).get_edges()
        runtime_edges = runtime_profile.get_node(node).get_edges()

        # Iterate through the edges from the runtime profile
        for runtime_domain in runtime_edges:
            # Get the leaves for the selected domain from the runtime profile
            runtime_leaves = runtime_profile.get_node(node).get_leaves(runtime_domain)
            
            # Iterate through all the edges of the MUD profile
            for mud_edge in mud_edges:
                # Get the leaves for the selected domain from the MUD profile
                mud_leaves = mud_profile.get_node(node).get_leaves(mud_edge)

                for runtime_leaf in runtime_leaves:
                    # Get the src IP and dst IP and retreive the hostnames.
                    runtime_sip_domain = get_hostname(runtime_leaf.sip)
                    runtime_dip_domain = get_hostname(runtime_leaf.dip)
            
                    for mud_leaf in mud_leaves:
                        # Set the values in this tuple to False
                        (sip_match, dip_match, sport_match, dport_match, proto_match) = [False]*5

                        # Get the type of IP info in the MUD profile (IPv4/IPv6/Domain/subnet)
                        mud_sip_type = get_ip_type(mud_leaf.sip)
                        mud_dip_type = get_ip_type(mud_leaf.dip)

                        # compare the source IPs directly
                        if mud_leaf.sip == "*" or mud_leaf.sip == runtime_leaf.sip:
                            sip_match = True
                        # if the MUD IP is a subnet, check if the runtime IP is in the subnet
                        elif mud_sip_type == IP_TYPES[3] and is_ip_in_subnet(runtime_leaf.sip, mud_leaf.sip):
                            sip_match = True
                        # if it is a domain/hostname check in 2 ways:
                        elif mud_sip_type == IP_TYPES[0]:
                            # get the src ip from the domain to match it to the runtime src ip
                            if get_ip_from_domain(mud_leaf.sip) == runtime_leaf.sip:
                                sip_match = True
                            # get the domain from the runtime sip, and match with the mud domain
                            elif mud_leaf.sip == runtime_sip_domain:
                                sip_match = True
                        
                        # compare the destination IPs directly
                        if mud_leaf.dip == "*" or mud_leaf.dip == runtime_leaf.dip:
                            dip_match = True
                        # if the MUD IP is a subnet, check if the runtime IP is in the subnet
                        elif mud_dip_type == IP_TYPES[3] and is_ip_in_subnet(runtime_leaf.dip, mud_leaf.dip):
                            dip_match = True
                        # if it is a domain/hostname type check in 2 ways:
                        elif mud_dip_type == IP_TYPES[0]:
                            # get the dst ip from the domain to match it to the runtime dst ip
                            if get_ip_from_domain(mud_leaf.dip) == runtime_leaf.dip:
                                dip_match = True
                            # get the domain from the runtime dip, and match with the mud domain
                            elif mud_leaf.dip == runtime_dip_domain:
                                dip_match = True
                        
                        # compare the src ports
                        if mud_leaf.sport == "*" or mud_leaf.sport == runtime_leaf.sport:
                            sport_match = True
                        
                        # compare the dst ports
                        if mud_leaf.dport == "*" or mud_leaf.dport == runtime_leaf.dport:
                            dport_match = True

                        # compare the protocols
                        if mud_leaf.proto == runtime_leaf.proto:
                            proto_match = True
                        
                        # if all are true, add to the matches list
                        if sip_match and dip_match and sport_match and dport_match and proto_match:
                            matches.append((runtime_domain, runtime_leaf))
    
    # print(matches)
    return matches

