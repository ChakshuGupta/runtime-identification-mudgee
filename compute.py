from collections import OrderedDict

from objects.leaf import Leaf
from objects.node import Node
from objects.tree import Tree


def compute_similarity_scores(mud_profiles, runtime_profile):
    """
    """
    dynamic_scores = {}
    static_scores = {}

    for device in mud_profiles:

        dynamic_scores[device] = compute_dynamic_similarity(mud_profiles[device], runtime_profile)
        static_scores[device] = compute_static_similarity(mud_profiles[device], runtime_profile)
    
    dynamic_scores = OrderedDict(reversed(list(dynamic_scores.items())))
    static_scores = OrderedDict(reversed(list(static_scores.items())))

    return dynamic_scores, static_scores


def compute_dynamic_similarity(mud_profile, runtime_profile):
    """
    """
    score = 0
    
    matches = get_intersection(mud_profile, runtime_profile)
    num_leaves = runtime_profile.get_num_leaves()

    score = len(matches) / num_leaves

    return score


def compute_static_similarity(mud_profile, runtime_profile):
    """
    """
    score = 0

    matches = find_intersection(mud_profile, runtime_profile)
    num_leaves = mud_profile["flows"].get_num_leaves()

    score = len(matches) / num_leaves
    
    return score


def find_intersection(mud_profile, runtime_profile):
    """
    """
    matches = []

    return matches

