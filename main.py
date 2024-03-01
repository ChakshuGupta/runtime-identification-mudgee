import sys
import yaml

from src.profile_handling import load_mud_profiles, runtime_profile_generation


if __name__ == "__main__":
    config = sys.argv[1]
    with open(config, 'r') as cfgfile:
        cfg = yaml.load(cfgfile, Loader=yaml.Loader)

    mud_profiles = load_mud_profiles(cfg["dir-mud-profiles"])

    device_matched = runtime_profile_generation(cfg, mud_profiles)
    print("Device ", cfg["device-name"], " matched to --- ", device_matched)