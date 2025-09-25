# Define base path constants

ROOT_BASE = "C:/users/image/code_projects/"
DEV_BASE = ROOT_BASE + "_DEV/"
PROD_BASE = ROOT_BASE + "_PROD/"
WAMP_BASE = "D:/wmap64/www/Project/"

DEV_CACHE = DEV_BASE + "_cache/"
WAMP_CACHE = WAMP_BASE + "_cache/"
PROD_CACHE = PROD_BASE + "_cache/"


def parse_args():
    import argparse

    parser = argparse.ArgumentParser(prog='deploy-dev', description="Deploy project from dev to wamp for testing.")
    parser.add_argument("project", type=str, help="Name of the project to deploy.")
    parser.add_argument("--PROD", action="store_true", help="Deploy to production server instead of DEV.")
    args = parser.parse_args()
    return args.project, args.PROD

def check_dirs(name):
    import os

    dev_path = DEV_BASE + name + "/"
    prod_path = PROD_BASE + name + "/"
    wamp_path = WAMP_BASE + name + "/"
    dCache = DEV_CACHE + name + "/"
    wCache = WAMP_CACHE + name + "/"
    pCache = PROD_CACHE + name + "/"

    for base in [dev_path, prod_path, wamp_path, dCache, wCache, pCache]:
        if not os.path.exists(base):
            print(f"Creating project directory '{base}'...")
            os.makedirs(base)
    return True

def cache_files(name, PROD=False):
    import os
    import shutil

    if PROD:
        prod_path = PROD_BASE + name + "/"
        pCache = PROD_CACHE + name + "/"
        if not os.path.exists(prod_path):
            print(f"Production path '{prod_path}' does not exist.")
            print(f"Creating directory '{prod_path}'...")
            os.makedirs(prod_path)
        # Copy files from prod to cache
        for item in os.listdir(prod_path):
            src = os.path.join(prod_path, item)
            dest = os.path.join(pCache, item)
            try:
                shutil.move(src, dest)
            except Exception as e:
                print(f"Destination '{dest}' present, dumping contents and trying again...")
                shutil.rmtree(dest)
                shutil.move(src, dest)
        print(f"Production Project '{name}' cached successfully from production.")
        return

    dev_path = DEV_BASE + name + "/"
    wamp_path = WAMP_BASE + name + "/"

    dCache = DEV_CACHE + name + "/"
    wCache = WAMP_CACHE + name + "/"


    # Copy files from dev to cache
    for item in os.listdir(dev_path):
        src = os.path.join(dev_path, item)
        dest = os.path.join(dCache, item)
        try:
            shutil.move(src, dest)
        except Exception as e:
            print(f"Destination '{dest}' present, dumping contents and trying again...")
            shutil.rmtree(dest)
            shutil.move(src, dest)

    # Copy files from wamp to cache
    for item in os.listdir(wamp_path):
        src = os.path.join(wamp_path, item)
        dest = os.path.join(wCache, item)
        try:
            shutil.move(src, dest)
        except Exception as e:
            print(f"Destination '{dest}' present, dumping contents and trying again...")
            shutil.rmtree(dest)
            shutil.move(src, dest)

    print(f"Project '{name}' cached successfully.")

def deploy_files(name, PROD=False):
    import os
    import shutil

    if PROD:
        prod_path = PROD_BASE + name + "/"
        build_path = ROOT_BASE + name + "/build/client/"

        if not os.path.exists(prod_path):
            print(f"Production path '{prod_path}' does not exist.")
            print(f"Creating directory '{prod_path}'...")
            os.makedirs(prod_path)

        # Copy files from build to prod
        for item in os.listdir(build_path):
            src = os.path.join(build_path, item)
            dest = os.path.join(prod_path, item)
            if os.path.isdir(src):
                shutil.copytree(src, dest, dirs_exist_ok=True)
            else:
                shutil.copy2(src, dest)

        print(f"Production Project '{name}' deployed successfully to production.")
        return

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
    [project_name, PROD] = parse_args()
    if check_dirs(project_name):
        cache_files(project_name, PROD=PROD)
        deploy_files(project_name, PROD=PROD)
    else:
        print("Directory check failed. Deployment aborted.")