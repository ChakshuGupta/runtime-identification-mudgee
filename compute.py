import socket

from collections import OrderedDict
# from ipaddress import ip_address

from constants import IP_TYPES
from objects.leaf import Leaf
from objects.node import Node
from objects.tree import Tree

from utils import get_ip_type, get_domain, get_ip_from_domain, is_ip_in_subnet

def compute_similarity_scores(mud_profiles, runtime_profile):
    """
    """
    dynamic_scores = {}
    static_scores = {}

    for device in mud_profiles:
        print("\n Checking device: ", device)
        matches = find_intersection(mud_profiles[device], runtime_profile)
        dynamic_scores[device] = compute_dynamic_similarity(matches, runtime_profile)
        static_scores[device] = compute_static_similarity(matches, mud_profiles[device])
    
    dynamic_scores = OrderedDict(reversed(list(dynamic_scores.items())))
    static_scores = OrderedDict(reversed(list(static_scores.items())))

    return dynamic_scores, static_scores


def compute_dynamic_similarity(matches, runtime_profile):
    """
    """
    score = 0

    num_leaves = runtime_profile.get_num_leaves()
    score = len(matches) / num_leaves

    print("Dynamic score: ", score)

    return score


def compute_static_similarity(matches, mud_profile):
    """
    """
    score = 0

    num_leaves = mud_profile.get_num_leaves()
    score = len(matches) / num_leaves

    print("Static score: ", score)
    
    return score


def find_intersection(mud_profile, runtime_profile):
    """
    Find overlapping sections between the two profiles and return the list of
    overlapping branches
    """
    matches = []

    nodes = mud_profile.get_all_nodes()

    for node in nodes:
        if runtime_profile.get_node(node) == None:
            continue

        mud_edges = mud_profile.get_node(node).get_edges()
        runtime_edges = runtime_profile.get_node(node).get_edges()

        for runtime_edge in runtime_edges:
            runtime_leaves = runtime_profile.get_node(node).get_leaves(runtime_edge)

            for mud_edge in mud_edges:
                mud_leaves = mud_profile.get_node(node).get_leaves(mud_edge)

                for runtime_leaf in runtime_leaves:

                    runtime_sip_domain = get_domain(runtime_leaf.sip)
                    runtime_dip_domain = get_domain(runtime_leaf.dip)
            
                    for mud_leaf in mud_leaves:
                        (sip_match, dip_match, sport_match, dport_match, proto_match) = [False]*5

                        mud_sip_type = get_ip_type(mud_leaf.sip)
                        mud_dip_type = get_ip_type(mud_leaf.dip)
                    
                        if mud_leaf.sip == "*" or mud_leaf.sip == runtime_leaf.sip:
                            sip_match = True
                        elif mud_sip_type == IP_TYPES[3] and is_ip_in_subnet(runtime_leaf.sip, mud_leaf.sip):
                            sip_match = True
                        elif mud_sip_type == IP_TYPES[0]:
                            if get_ip_from_domain(mud_leaf.sip) == runtime_leaf.sip:
                                sip_match = True
                            elif mud_leaf.sip == runtime_sip_domain:
                                sip_match = True
                        
                        if mud_leaf.dip == "*" or mud_leaf.dip == runtime_leaf.dip:
                            dip_match = True
                        elif mud_dip_type == IP_TYPES[3] and is_ip_in_subnet(runtime_leaf.dip, mud_leaf.dip):
                            dip_match = True
                        elif mud_dip_type == IP_TYPES[0]:
                            if get_ip_from_domain(mud_leaf.dip) == runtime_leaf.dip:
                                dip_match = True
                            elif mud_leaf.dip == runtime_dip_domain:
                                dip_match = True
                        
                        if mud_leaf.sport == "*" or mud_leaf.sport == runtime_leaf.sport:
                            sport_match = True
                        
                        if mud_leaf.dport == "*" or mud_leaf.dport == runtime_leaf.dport:
                            dport_match = True

                        if mud_leaf.proto == runtime_leaf.proto:
                            proto_match = True
                        
                        if sip_match and dip_match and sport_match and dport_match and proto_match:
                            matches.append((runtime_edge, runtime_leaf))
    
    # print(matches)
    return matches

