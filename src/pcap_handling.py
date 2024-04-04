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

    dns_cache = dict()

    packets = list()
    # Traverse through the list of raw packets and create packet objects
    for packet in raw_packets:
        
        packets.append(Packet(packet))

        if packet.haslayer("DNS"):
            if packet["DNS"].an is not None:
                for i in range(packet["DNS"].ancount):
                    if packet["DNS"].an[i].type in [1, 5]:
                        rrname = packet["DNS"].an[i].rrname.decode("utf-8")
                        dns_cache[packet["DNS"].an[i].rdata] = rrname
                        if rrname in dns_cache.keys():
                            dns_cache[packet["DNS"].an[i].rdata] = dns_cache[rrname]
    
    return packets, dns_cache
