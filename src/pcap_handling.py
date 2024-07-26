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
    dns_cache: {IP: domain name}

    """

    print("##### Reading PCAP file: ", pcap_file)
    # Read the raw packets using scapy
    raw_packets = rdpcap(pcap_file)

    # Create an empty DNS cache {IP: domain name}
    dns_cache = dict()

    packets = list()
    # Traverse through the list of raw packets and create packet objects
    for packet in raw_packets:
        
        packet_obj = Packet(packet)
        if packet_obj.is_none():
            # If the packet type is not UDP or TCP, packet object will be none.
            continue
        packets.append(packet_obj)

        # Generate the DNS cache from the packets
        if packet.haslayer("DNS"):
            # Check if the packet has an answer to a DNS query
            if packet["DNS"].an is not None and len(packet["DNS"].an) > 0:
                for i in range(packet["DNS"].ancount):
                    # Check if the answer type is A or CNAME
                    if packet["DNS"].an[i].type in [1, 5]:
                        rrname = packet["DNS"].an[i].rrname.decode("utf-8").strip(".")
                        dns_cache[packet["DNS"].an[i].rdata] = rrname
                        if rrname in dns_cache.keys():
                            dns_cache[packet["DNS"].an[i].rdata] = dns_cache[rrname]
    
    return packets, dns_cache
