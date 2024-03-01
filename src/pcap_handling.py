import os
from scapy.all import *

from src.objects.flow import Flow
from src.objects.packet import Packet


def get_pcaps_from_dir(input_dir):
    """
    Returns the list of pcap/pcapng files from the input directory
    """
    pcap_list = list()
    if not os.path.exists(input_dir):
        print("ERROR! Path to dataset {} doesn't exist.".format(input_dir))
        return pcap_list
    
    for root, dirs, files in os.walk(input_dir):
        for file in files:
                if file.endswith(".pcap") or file.endswith(".pcapng"):
                    pcap_list.append(os.path.join(root, file))
    
    return pcap_list


def read_pcap(pcap_file):
    """
    Read pcap file and return the list of packets
    
    [Args]
    pcap_file: path to pcap file to read

    [Returns]
    packets: List of packets

    """

    print("##### Reading PCAP file: ", pcap_file)
    # Read the raw packets using scapy
    raw_packets = rdpcap(pcap_file)

    packets = list()
    # Traverse through the list of raw packets and create packet objects
    for packet in raw_packets:
        packets.append(Packet(packet))
    
    return packets
