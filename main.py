import sys
import time
import yaml

from src.profile_handling import load_mud_profiles, runtime_profile_generation


if __name__ == "__main__":
    config = sys.argv[1]
    with open(config, 'r') as cfgfile:
        cfg = yaml.load(cfgfile, Loader=yaml.Loader)

    mud_profiles = load_mud_profiles(cfg["dir-mud-profiles"])

    start_time = time.time()
    dynamic_matches, static_matches = runtime_profile_generation(cfg, mud_profiles)
    end_time = time.time()
    print("Device ", cfg["device-name"], " matched to --- ", dynamic_matches[-1], static_matches[-1])
    print("Runtime to get the match: ", end_time- start_time)