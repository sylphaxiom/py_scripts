
# Define base paths
root_base = "C:/users/image/code_projects/"
dev_base = root_base + "_DEV/"
wamp_base = "D:/wamp64/www/Project/"
cache_base = "../_cache/"

import argparse

def parse_args():
    parser = argparse.ArgumentParser(prog='deploy-dev', description="Deploy project from dev to wamp for testing.")
    parser.add_argument("project", type=str, help="Name of the project to deploy.")
    args = parser.parse_args()
    return args

def cache_files(name):
    import os
    import shutil

    dev_path = dev_base + name + "/"
    wamp_path = wamp_base + name + "/"
    cache_path = cache_base + name + "/"

    if not os.path.exists(dev_path):
        print(f"Development path '{dev_path}' does not exist.")
        print(f"Creating directory '{dev_path}'")
        os.makedirs(dev_path)
        return

    if not os.path.exists(wamp_path):
        print(f"WAMP path '{wamp_path}' does not exist.")
        print(f"Creating directory '{wamp_path}'")
        os.makedirs(wamp_path)
        return

    if not os.path.exists(cache_path):
        os.makedirs(cache_path)

    # Copy files from dev to cache
    for item in os.listdir(dev_path):
        src = os.path.join(dev_path, item)
        dest = os.path.join(cache_path, item)
        if os.path.isdir(src):
            shutil.copytree(src, dest, dirs_exist_ok=True)
        else:
            shutil.copy2(src, dest)

    # Copy files from wamp to cache
    for item in os.listdir(wamp_path):
        src = os.path.join(wamp_path, item)
        dest = os.path.join(cache_path, item)
        if os.path.isdir(src):
            shutil.copytree(src, dest, dirs_exist_ok=True)
        else:
            shutil.copy2(src, dest)

    print(f"Project '{name}' cached successfully.")