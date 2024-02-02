import os
import sys
import yaml

from compute import compute_similarity_scores
from read_pcap import *
from utils import read_csv, read_json
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
                mud_profiles[device_name]["flows"] = generate_mud_profile_tree( flows, device_name)
            elif "Mud" in file:
                mud_profiles[device_name]["profiles"] = read_json(os.path.join(root, file))
            else:
                continue
    return mud_profiles


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
    runtime_profile = Tree(device_name)
    # Traverse the packets in the list
    for packet in packets:
        # Check if packet has none fields
        if packet.is_none():
            continue
        in_time = packet.time - start_time
        if in_time > epoch_time:
            in_time = 0
            start_time = start_time + epoch_time
            
            update_runtime_profile(flows, runtime_profile)

            dynamic_scores, static_scores = compute_similarity_scores(mud_profiles, runtime_profile)

        # Generate a key using packet protocol and a frozen set of source IP and destination IP
        # Using frozenset to ensure the key is hashable (a requirement for dict keys)
        key = (packet.proto, frozenset({packet.sip, packet.dip}))
        # Add a the packet to the flow
        flows[key] = flows.get(key, Flow()).add(packet)

    runtime_profile.print()


if __name__ == "__main__":
    config = sys.argv[1]
    with open(config, 'r') as cfgfile:
        cfg = yaml.load(cfgfile, Loader=yaml.Loader)

    mud_profiles = load_mud_profiles(cfg["dir-mud-profiles"])

    runtime_profile_generation(cfg["dir-pcaps"], mud_profiles, cfg["device-name"])