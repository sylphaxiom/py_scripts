# Define base path constants
ROOT_BASE = "C:/users/image/code_projects/"
DEV_BASE = f"{ROOT_BASE}_DEV/"
PROD_BASE = f"{ROOT_BASE}_PROD/"
WAMP_BASE = "D:/wmap64/www/Project/"
PROD_REMOTE = "/home2/xikihgmy/public_html/"
DEV_REMOTE = "/home2/xikihgmy/test/"
DND_REMOTE = "/home2/xikihgmy/dnd/"
API_SECURE = "/home2/xikihgmy/includes/"
API_BASE = f"{ROOT_BASE}_API/"
DEV_CACHE = f"{DEV_BASE}_cache/"
WAMP_CACHE = f"{WAMP_BASE}_cache/"
PROD_CACHE = f"{PROD_BASE}_cache/"
API_CACHE =  f"{API_BASE}_cache/"


def parse_args():
    import argparse

    parser = argparse.ArgumentParser(prog='deploy-dev', description="Deploy project from dev to wamp for testing.")
    parser.add_argument("project", type=str, help="Name of the project to deploy.")
    parser.add_argument("--PROD", action="store_true", help="Deploy to production server instead of DEV.")
    parser.add_argument("--API", action="store_true", help="Deploy APIs")
    parser.add_argument("--DEV", action="store_true", help="Deploy to Dev environment on web host.")
    args = parser.parse_args()
    return args.project, args.PROD, args.API, args.DEV

def setup(name):
    import os
    import subprocess

    dev_path = f"{DEV_BASE}{name}/"
    prod_path = f"{PROD_BASE}{name}/"
    wamp_path = f"{WAMP_BASE}{name}/"
    api_path = f"{API_BASE}{name}/"
    dCache = f"{DEV_CACHE}{name}/"
    wCache = f"{WAMP_CACHE}{name}/"
    pCache = f"{PROD_CACHE}{name}/"
    aCache = f"{API_CACHE}{name}/"

    for base in [dev_path, prod_path, wamp_path, api_path, dCache, wCache, pCache, aCache]:
        if not os.path.exists(base):
            print(f"Creating project directory '{base}'...")
            os.makedirs(base)

    print("running playwright tests...")
    subprocess.check_call('npx playwright test --quiet --retries 2 --last-failed', shell=True)

    return True

def check_files(name,PROD=False,DEV=False):
    import os
    import json
    import shutil
    # Use this function to make any temporary (or perminent)
    # changes to your files. For instance, I have URLs that change
    # depending on where the files go. If I push to DEV, a set of 
    # values are needed and the same for PROD. This function
    # will make the necessary changes to the files, push them,
    # then revert the files after the push. This requires no changes
    # in the dev environment. This script will look for a file named
    # mods.json which will contain a list of dicts as 
    # {filename:"<file>",search:"<search>",update:"<update>",PROD?:bool,DEV?:bool}
    # base path is assumed to be "/src/"

    PATH_BASE = f"{ROOT_BASE}{name}/"
    SRC = f"{PATH_BASE}src/"
    TEMP = f"{PATH_BASE}temp/"
    trashCan = []

    with open(f"{PATH_BASE}mods.json","r") as file:
        mods = json.load(file)
    if not os.path.exists(TEMP):
        os.mkdir(TEMP)
    for mod in mods:
        filename = mod['filename']
        file = f"{SRC}{filename}" #contains full path
        search = mod['search']
        update = mod['update']
        isProd = mod.get("PROD")
        isDev = mod.get("DEV")
        if filename.find("/"):
            filename = filename.split("/")[-1]
        backup = f"{TEMP}{filename}"

        if PROD and not isProd:
            continue
        if DEV and not isDev:
            continue

        cp = shutil.copyfile(src=file,dst=backup)
        assert cp == backup ,f"An error must have occurred, {cp} is different from {backup}"
        contents = ''
        with open(file) as original:
            for line in original:
                newLine = ''
                if line.find(search) != -1:
                    print(f"Found a change in {filename} for {search}")
                    newLine = line.replace(search, update)
                    print(f"Adding {filename} to cleanup")
                    if file not in trashCan:
                        trashCan.append(file)
                else:
                    newLine = line
                contents += newLine
        with open(file,"w") as original:
            original.write(contents)
    return trashCan

def cleanup(trashCan, name):
    import os
    import shutil
    import subprocess

    PATH_BASE = f"{ROOT_BASE}{name}/"
    TEMP = f"{PATH_BASE}temp/"

    for trash in trashCan:
        filename = trash.split("/")[-1]
        tmpFile = f"{TEMP}{filename}"
        shutil.copyfile(src=tmpFile,dst=trash)
        os.remove(tmpFile)
    os.rmdir(TEMP)
    subprocess.check_call('npm run clean', shell=True)    
    print("Cleanup complete")

def cache_files(name, PROD=False, API=False):
    import os
    import shutil

    if PROD:
        prod_path = f"{PROD_BASE}{name}/"
        pCache = f"{PROD_CACHE}{name}/"
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
        prod_path = f"{PROD_BASE}{name}/"
        build_path = f"{ROOT_BASE}{name}/build/client/"

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
        api_path = f"{API_BASE}{name}/"
        build_path = f"{ROOT_BASE}{name}/src/api/v1/"

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

    dev_path = f"{DEV_BASE}{name}/"
    wamp_path = f"{WAMP_BASE}{name}/"
    build_path = f"{ROOT_BASE}{name}/build/client/"

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
        if name == "DnD-app":
            REMOTE = DND_REMOTE
        else:
            REMOTE = PROD_REMOTE
        location = 'Production'
    elif API:
        path = api_path
        if name == "DnD-app":
            REMOTE = DND_REMOTE + "api/v1/"
        elif DEV:
            REMOTE = DEV_REMOTE + "api/v1/"
        else:
            REMOTE = PROD_REMOTE + "api/v1/"
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
        if file.name in ["bucket.php","kothis.DB_make.sql","sylphaxiom.DB_make.sql"]:
            sftp.put(f"{path}/{file.name}", f"{API_SECURE}{file.name}" )
            print( f"{file.name} moved to {location} successfully" )
            continue
        if file.is_file():
            sftp.put( f"{path}/{file.name}", f"{REMOTE}{file.name}" )
            print(f"{file.name} moved to {location} successfully" )
        if file.is_dir():
            subdir = os.scandir( f"{path}/{file.name}" )
            try:
                sftp.listdir(f"{REMOTE}{file.name}")
            except:
                print(f"Remote directory {REMOTE}{file.name} is missing, please add directory to continue...")
                input("Press Enter to continue...")
            for subfile in subdir:
                sftp.put( f"{path}/{file.name}/{subfile.name}", f"{REMOTE}{file.name}/{subfile.name}" )
                print(f"{subfile.name} moved to {location} subdirectory {file.name} successfully" )
    
if __name__ == "__main__":
    [project_name, PROD, API, DEV] = parse_args()
    if setup(project_name):
        cache_files(project_name, PROD=PROD, API=API)
        deploy_files(project_name, PROD=PROD, API=API)
        if (PROD):
            trash = check_files(project_name, PROD=PROD)
            ftp_prod(project_name, PROD=PROD)
        if (API):
            ftp_prod(project_name, API=API)
        if (DEV):
            trash = check_files(project_name, DEV=DEV)
            ftp_prod(project_name, DEV=DEV)
    else:
        print("Directory check failed. Deployment aborted.")
    cleanup(trash,project_name) #Cleanup no matter what :)