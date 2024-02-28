import os
import sys
import yaml

from compute import compute_similarity_scores
from pcap_handling import *
from utils import read_json
from tree_handling import update_runtime_profile, generate_mud_profile_tree

from objects.flow import Flow
from objects.tree import Tree      


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
        # mud_profiles[device_name] = dict()
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
    
    if len(pcap_list) == 0:
        return None
    
    packets = list()
    for pcap in pcap_list:
        packets.extend(read_pcap(pcap))
    
    # Order read packets using time
    packets  = sorted(packets, key=lambda ts: ts.time)
    
    # initialise time values
    start_time = packets[0].time # time of the first packet
    end_time = packets[-1].time # time of the last packet
    epoch_time = 900000 # = 15 minutes
    in_time = 0 # time passed since the beginning of the epoch

    # print the duration of the packet capture
    print("\n\n------- Total time: " + str(end_time - start_time) + " -------\n\n")

    flows = dict()
    runtime_profile = Tree(config["device-name"], config["default-gateway-ip"])

    device_matched = ""
    # Traverse the packets in the list
    for packet in packets:
        # Check if packet has none fields
        if packet.is_none():
            continue
        
        # get the time passed since start of the epoch
        in_time = packet.time - start_time
        
        if in_time > epoch_time:
            # if the time pass has crossed epoch compute similarity scores
            # it is not ">=", since we still want to add packets to the flows till 
            # we are reach the epoch

            in_time = 0
            start_time = start_time + epoch_time
            
            update_runtime_profile(flows, runtime_profile)

            dynamic_scores, static_scores = compute_similarity_scores(mud_profiles, runtime_profile)
            print("Highest dynamic score : ", dynamic_scores[-1])
            print("Highest static score : ", static_scores[-1])

            if dynamic_scores[-1][1] == 1:
                print("Match Found!", dynamic_scores[-1][0])
                device_matched = (dynamic_scores[-1])
                break
            elif static_scores[-1][1] == 1:
                print("Match Found!", static_scores[-1][0])
                device_matched = (static_scores[-1])
                break


        # Generate a key using packet protocol and a frozen set of source IP and destination IP
        # Using frozenset to ensure the key is hashable (a requirement for dict keys)
        key = (packet.proto, frozenset({packet.sip, packet.dip, packet.sport, packet.dport}))
        # Add a the packet to the flow
        flows[key] = flows.get(key, Flow()).add(packet)
    
    device_matched = dynamic_scores[-1]

    runtime_profile.print()
    return device_matched


if __name__ == "__main__":
    config = sys.argv[1]
    with open(config, 'r') as cfgfile:
        cfg = yaml.load(cfgfile, Loader=yaml.Loader)

    mud_profiles = load_mud_profiles(cfg["dir-mud-profiles"])

    device_matched = runtime_profile_generation(cfg, mud_profiles)
    print("Device ", cfg["device-name"], " matched to --- ", device_matched)