import os

from src.compute import compute_similarity_scores
from src.constants import EPOCH_TIME
from src.objects.flow import Flow
from src.objects.tree import Tree  
from src.pcap_handling import *
from src.tree_handling import update_runtime_profile, generate_mud_profile_tree
from src.utils import read_json, get_hostname
   

def load_mud_profiles(model_dir):
    """
    Load the MUD profiles generated during the training phase.
    """
    mud_profiles = dict()
    for root, dirs, files in os.walk(model_dir):
        if os.path.samefile(root, model_dir):
            continue
        device_name = os.path.basename(root)
        for file in files:
            if "Mud" in file:
                mud_profiles[device_name] = generate_mud_profile_tree(
                                                                read_json(
                                                                    os.path.join(root, file)
                                                                    )
                                                                )
            else:
                continue
    return mud_profiles


def runtime_profile_generation(config, mud_profiles):
    """
    Generate the runtime profile from the input packets
    """
    pcap_list = get_pcaps_from_dir(config["dir-pcaps"])
    
    if pcap_list is None or len(pcap_list) == 0:
        return None
    
    if mud_profiles is None or len(mud_profiles) == 0:
        return None
    
    flows = dict()
    runtime_profile = Tree(config["device-name"], config["default-gateway-ip"])

    pcap_list = sorted(pcap_list)
    print(pcap_list)

    matches_dynamic = []
    matches_static = []
    dynamic_scores, static_scores = None, None

    dns_cache = dict()
    
    start_time = 0
    end_time = 0
    index = 0

    for pcap in pcap_list:
        print(pcap)
        packets, temp_dns_cache = read_pcap(pcap)
        dns_cache.update(temp_dns_cache)
        
        if index == 0 or end_time - start_time >= EPOCH_TIME:
            # initialise time values
            start_time = packets[0].time # time of the first packet
            end_time = packets[-1].time

        # Traverse the packets in the list
        for packet in packets:
            # Check if packet has none fields
            if packet.is_none():
                print("Packet is none")
                continue
            # get the time passed since start of the epoch
            in_time = packet.time - start_time
            
            # Generate a key using packet protocol and a frozen set of source IP and destination IP and ports
            # Using frozenset to ensure the key is hashable (a requirement for dict keys)
            key = (packet.proto, frozenset({packet.sip, packet.dip}))
            # Add a the packet to the flow
            flows[key] = flows.get(key, Flow()).add(packet)
            # Set domain for the source IP and destination IP
            flows[key].set_domain(packet.sip, dns_cache.get(packet.sip, None))
            flows[key].set_domain(packet.dip, dns_cache.get(packet.dip, None))
            
            if in_time >= EPOCH_TIME:
                # if the time pass has crossed epoch compute similarity scores
                print("Time passed: " + str(in_time))

                in_time = 0
                start_time = packet.time

                old_num_leaves = runtime_profile.get_num_leaves()                
                update_runtime_profile(flows, runtime_profile)
                new_num_leaves = runtime_profile.get_num_leaves()                

                if new_num_leaves != old_num_leaves:
                    dynamic_scores, static_scores = compute_similarity_scores(mud_profiles, runtime_profile)
                    print(dynamic_scores, static_scores)

                    if len(dynamic_scores) > 0 and len(static_scores) > 0:

                        print("Highest dynamic score : ", dynamic_scores[0])
                        print("Highest static score : ", static_scores[0])
                        
                        winner_dynamic = {}
                        winner_dynamic[dynamic_scores[0][1]]=[]
                        for device, score in dynamic_scores:
                            if score not in winner_dynamic.keys():
                                continue
                            winner_dynamic[score].append(device)
                        
                        winner_static = {}
                        winner_static[static_scores[0][1]]=[]
                        for device, score in static_scores:
                            if score not in winner_static.keys():
                                continue
                            winner_static[score].append(device)
                        
                        print(winner_dynamic)
                        print(winner_static)
                        
                        matches_dynamic.append(winner_dynamic)
                        matches_static.append(winner_static)

                        if dynamic_scores[-1][1] == 1:
                            print("Match Found!", dynamic_scores[-1][0])
                            
                        elif static_scores[-1][1] == 1:
                            print("Match Found!", static_scores[-1][0])
                            
        index += 1
    
    print("Dynamic matches for every epoch", matches_dynamic)
    print("Static matches for every epoch", matches_static)

    runtime_profile.print()
    return matches_dynamic, matches_static