from ipaddress import ip_address

from utils import get_domain, is_valid_hostname
from objects.leaf import Leaf
from objects.node import Node
from objects.tree import Tree 


def add_to_node(comp, dir, mud_tree, flow):
    """
    Add flow to the tree. This adds a new node or adds edges and/or leaves
    to existing nodes.
    """
    node_name = dir + " " + comp
    node = mud_tree.get_node(node_name)
    if node is None:
        node = Node(comp, dir)

    leaf = Leaf()
    leaf.set_from_profile(flow)

    if dir == "to":
        domain = get_domain(flow.dip)
        node.add_leaf(leaf, domain)
    elif dir == "from":
        domain = get_domain(flow.sip)
        node.add_leaf(leaf, domain)

    mud_tree.add_node(node)


def update_node(comp, dir, mud_tree, flow):
    """
    Update the node in the tree. This adds a new node or adds edges and/or leaves
    to existing nodes.
    """
    node_name = dir + " " + comp
    node = mud_tree.get_node(node_name)
    if node is None:
        add_to_node(comp, dir, mud_tree, flow)

    if dir == "to":
        domain = get_domain(flow.dip)
        leaves = node.get_leaves(domain)

    elif dir == "from":
        domain = get_domain(flow.sip)
        leaves = node.get_leaves(domain)
    
    else: # Probably not needed. Just to cover all cases
        return ValueError

    new_leaf = Leaf()
    new_leaf.set_from_profile(flow)

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


def update_runtime_profile(flows, profile_tree):
    if profile_tree.is_empty():
        # generate the initial tree
        for flow in flows:
            print(flows[flow].sip, flows[flow].dip)
            if ip_address(flows[flow].sip).is_private:
                comp = "Local"
                dir = "from"
            else:
                comp = "Internet"
                dir = "from"
            add_to_node(comp, dir, profile_tree, flows[flow])

            if ip_address(flows[flow].dip).is_private:
                comp = "Local"
                dir = "to"
            else:
                comp = "Internet"
                dir = "to"
            add_to_node(comp, dir, profile_tree, flows[flow])
        
        profile_tree.print()
    else:
        for flow in flows:
            print(flows[flow].sip, flows[flow].dip)
            if ip_address(flows[flow].sip).is_private:
                comp = "Local"
                dir = "from"
            else:
                comp = "Internet"
                dir = "from"
            update_node(comp, dir, profile_tree, flows[flow])

            if ip_address(flows[flow].dip).is_private:
                comp = "Local"
                dir = "to"
            else:
                comp = "Internet"
                dir = "to"
            update_node(comp, dir, profile_tree, flows[flow])
        
        profile_tree.print()


def generate_mud_tree(device_flows, device_name):
    """
    Generates the profile tree from the existing MUD profiles
    """
    mud_tree = Tree(device_name)
    for flow in device_flows:
        try:
            if flow.sip != "*" and ip_address(flow.sip).is_private:
                comp = "Local"
                dir = "from"
                add_to_node(comp, dir, mud_tree, flow)
                
            elif flow.sip!= "*":
            # else:
                comp = "Internet"
                dir = "from"
                add_to_node(comp, dir, mud_tree, flow)

        except ValueError:
            if is_valid_hostname(flow.sip):
                comp = "Internet"
                dir = "from"
                add_to_node(comp, dir, mud_tree, flow)

        try:

            if flow.dip!= "*" and ip_address(flow.dip).is_private:
                comp = "Local"
                dir = "to"
                add_to_node(comp, dir, mud_tree, flow)

            elif flow.dip!= "*":
            # else:
                comp = "Internet"
                dir = "to"
                add_to_node(comp, dir, mud_tree, flow)
            
            
        except ValueError:
            if is_valid_hostname(flow.dip):
                comp = "Internet"
                dir = "to"
                add_to_node(comp, dir, mud_tree, flow)
                
    # print(mud_tree.get_all_nodes())
    mud_tree.print()
    return mud_tree