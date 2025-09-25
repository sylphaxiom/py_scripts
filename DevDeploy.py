# Define base path constants
ROOT_BASE = "C:/users/image/code_projects/"
DEV_BASE = ROOT_BASE + "_DEV/"
WAMP_BASE = "D:/wmap64/www/Project/"
DEV_CACHE = DEV_BASE + "_cache/"
WAMP_CACHE = WAMP_BASE + "_cache/"


def parse_args():

    # Parse command line arguments for project name and return the project name

    import argparse

    parser = argparse.ArgumentParser(prog='deploy-dev', description="Deploy project from dev to wamp for testing.")
    parser.add_argument("project", type=str, help="Name of the project to deploy.")
    args = parser.parse_args()
    return args.project

def check_dirs(name):
    import os

    dev_path = DEV_BASE + name + "/"
    wamp_path = WAMP_BASE + name + "/"
    dCache = DEV_CACHE + name + "/"
    wCache = WAMP_CACHE + name + "/"

    for base in [dev_path, wamp_path, dCache, wCache]:
        if not os.path.exists(base):
            print(f"Creating project directory '{base}'...")
            os.makedirs(base)
    return True

def cache_files(name):
    import os
    import shutil

    dev_path = DEV_BASE + name + "/"
    wamp_path = WAMP_BASE + name + "/"

    dCache = DEV_CACHE + name + "/"
    wCache = WAMP_CACHE + name + "/"

    if not os.path.exists(dCache):
        print(f"Cache path '{dCache}' does not exist.")
        print(f"Creating directory '{dCache}'...")
        os.makedirs(dCache)

    if not os.path.exists(wCache):
        print(f"Cache path '{wCache}' does not exist.")
        print(f"Creating directory '{wCache}'...")
        os.makedirs(wCache)

    # Copy files from dev to cache
    for item in os.listdir(dev_path):
        src = os.path.join(dev_path, item)
        dest = os.path.join(dCache, item)
        shutil.move(src, dest)

    # Copy files from wamp to cache
    for item in os.listdir(wamp_path):
        src = os.path.join(wamp_path, item)
        dest = os.path.join(wCache, item)
        shutil.move(src, dest)

    print(f"Project '{name}' cached successfully.")

def deploy_files(name):

    import os
    import shutil

    dev_path = DEV_BASE + name + "/"
    wamp_path = WAMP_BASE + name + "/"
    build_path = ROOT_BASE + name + "/build/client/"

    if not os.path.exists(dev_path):
        print(f"Development path '{dev_path}' does not exist.")
        print(f"Creating directory '{dev_path}'...")
        os.makedirs(dev_path)

    if not os.path.exists(wamp_path):
        print(f"WAMP path '{wamp_path}' does not exist.")
        print(f"Creating directory '{wamp_path}'...")
        os.makedirs(wamp_path)
        
    # Copy files from build to dev
    for item in os.listdir(build_path):
        src = os.path.join(build_path, item)
        destDev = os.path.join(dev_path, item)
        destWamp = os.path.join(wamp_path, item)
        if os.path.isdir(src):
            shutil.copytree(src, destDev, dirs_exist_ok=True)
            shutil.copytree(src, destWamp, dirs_exist_ok=True)
        else:
            shutil.copy2(src, destDev)
            shutil.copy2(src, destWamp)

    print(f"Project '{name}' deployed successfully.")

if __name__ == "__main__":
    project_name = parse_args()
    if check_dirs(project_name):
        cache_files(project_name)
        deploy_files(project_name)
    else:
        print("Directory check failed. Deployment aborted.")