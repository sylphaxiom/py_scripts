# Define base path constants

ROOT_BASE = "C:/users/image/code_projects/"
DEV_BASE = ROOT_BASE + "_DEV/"
PROD_BASE = ROOT_BASE + "_PROD/"
WAMP_BASE = "D:/wmap64/www/Project/"
PROD_REMOTE = "/home2/xikihgmy/public_html/"
DEV_REMOTE = "/home2/xikihgmy/test/"
API_REMOTE = "/home2/xikihgmy/public_html/api/v1/"
API_SECURE = "/home2/xikihgmy/includes/"
API_BASE = ROOT_BASE + "_API/"
DEV_CACHE = DEV_BASE + "_cache/"
WAMP_CACHE = WAMP_BASE + "_cache/"
PROD_CACHE = PROD_BASE + "_cache/"
API_CACHE = API_BASE + "_cache/"


def parse_args():
    import argparse

    parser = argparse.ArgumentParser(prog='deploy-dev', description="Deploy project from dev to wamp for testing.")
    parser.add_argument("project", type=str, help="Name of the project to deploy.")
    parser.add_argument("--PROD", action="store_true", help="Deploy to production server instead of DEV.")
    parser.add_argument("--API", action="store_true", help="Deploy APIs")
    parser.add_argument("--DEV", action="store_true", help="Deploy to Dev environment on web host.")
    args = parser.parse_args()
    return args.project, args.PROD, args.API, args.DEV

def check_dirs(name):
    import os

    dev_path = DEV_BASE + name + "/"
    prod_path = PROD_BASE + name + "/"
    wamp_path = WAMP_BASE + name + "/"
    api_path = API_BASE + name + "/"
    dCache = DEV_CACHE + name + "/"
    wCache = WAMP_CACHE + name + "/"
    pCache = PROD_CACHE + name + "/"
    aCache = API_CACHE + name + "/"

    for base in [dev_path, prod_path, wamp_path, api_path, dCache, wCache, pCache, aCache]:
        if not os.path.exists(base):
            print(f"Creating project directory '{base}'...")
            os.makedirs(base)
    return True

def cache_files(name, PROD=False, API=False):
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
    
    if API:
        api_path = API_BASE + name + "/"
        aCache = API_CACHE + name + "/"
        if not os.path.exists(api_path):
            print(f"API path '{api_path}' does not exist.")
            print(f"Creating directory '{api_path}'...")
            os.makedirs(api_path)
        # Copy files from api to cache
        for item in os.listdir(api_path):
            src = os.path.join(api_path, item)
            dest = os.path.join(aCache, item)
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

def deploy_files(name, PROD=False, API=False):
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
    
    if API:
        api_path = API_BASE + name + "/"
        build_path = ROOT_BASE + name + "/src/api/v1/"

        if not os.path.exists(api_path):
            print(f"API path '{api_path}' does not exist.")
            print(f"Creating directory '{api_path}'...")
            os.makedirs(api_path)

        # Copy files from build to api
        for item in os.listdir(build_path):
            src = os.path.join(build_path, item)
            dest = os.path.join(api_path, item)
            if os.path.isdir(src):
                shutil.copytree(src, dest, dirs_exist_ok=True)
            else:
                shutil.copy2(src, dest)

        print(f"API for Project '{name}' deployed successfully to production.")
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

def ftp_prod(name, PROD=False, API=False, DEV=False):
    import paramiko as Ftp
    import os

    KEY_PATH = "C:/Users/image/.ssh/home_ssh"
    prod_path = PROD_BASE + name
    api_path = API_BASE + name
    dev_path = DEV_BASE + name

    if PROD:
        path = prod_path
        REMOTE = PROD_REMOTE
        location = 'Production'
    elif API:
        path = api_path
        REMOTE = API_REMOTE
        location = 'API'
    elif DEV:
        path = dev_path
        REMOTE = DEV_REMOTE
        location = 'Development'
    else:
        return(-1)

    # Build connection
    client = Ftp.SSHClient()
    client.set_missing_host_key_policy(Ftp.AutoAddPolicy())
    client.connect(
        hostname="50.6.18.187",
        username="xikihgmy",
        port=22,
        key_filename=KEY_PATH,
        passphrase="rabbit",
        look_for_keys=False
        )
    sftp = client.open_sftp()
    dir = os.scandir( path )
    for file in dir:
        if file.name in ["bucket.php","DB_make.sql"]:
            sftp.put( path + "/" + file.name, API_SECURE + file.name )
            print( file.name + " moved to " + location + " successfully" )
            continue
        if file.is_file():
            sftp.put( path + "/" + file.name, REMOTE + file.name )
            print( file.name + " moved to " + location + " successfully" )
        if file.is_dir():
            subdir = os.scandir( path + "/" + file.name )
            for subfile in subdir:
                sftp.put( path + "/" + file.name + "/" + subfile.name, REMOTE + file.name + "/" + subfile.name )
                print( subfile.name + " moved to " + location + " subdirectory " + file.name + " successfully" )
    
if __name__ == "__main__":
    [project_name, PROD, API, DEV] = parse_args()
    if check_dirs(project_name):
        cache_files(project_name, PROD=PROD, API=API)
        deploy_files(project_name, PROD=PROD, API=API)
        if (PROD):
            ftp_prod(project_name, PROD=PROD)
        if (API):
            ftp_prod(project_name, API=API)
        if (DEV):
            ftp_prod(project_name, DEV=DEV)
    else:
        print("Directory check failed. Deployment aborted.")