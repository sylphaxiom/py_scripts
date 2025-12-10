import posixpath as Unx
import ntpath as Win
import os
import subprocess
import argparse
import json
import shutil
import paramiko as Ftp
import pathlib
# Define base path constants

# Windows stype paths
ROOT_BASE = Win.realpath("C:\\Users\\image\\code_projects\\")
WAMP_BASE = Win.realpath("D:\\wmap64\\www\\Project\\")
DEV_BASE = Win.join(ROOT_BASE,"_DEV\\")
PROD_BASE = Win.join(ROOT_BASE,"_PROD\\")
API_BASE = Win.join(ROOT_BASE,"_API\\")
DEV_CACHE = Win.join(DEV_BASE,"_cache\\")
WAMP_CACHE = Win.join(WAMP_BASE,"_cache\\")
PROD_CACHE = Win.join(PROD_BASE,"_cache\\")
API_CACHE =  Win.join(API_BASE,"_cache\\")

# Unix style paths
PROD_REMOTE = Unx.realpath("/home2/xikihgmy/public_html/")
DEV_REMOTE = Unx.realpath("/home2/xikihgmy/test/")
DND_REMOTE = Unx.realpath("/home2/xikihgmy/dnd/")
API_SECURE = Unx.realpath("/home2/xikihgmy/includes/")

# Parse CLI arguments
def parse_args():

    parser = argparse.ArgumentParser(prog='deploy-dev', description="Deploy project from dev to wamp for testing.")
    parser.add_argument("project", type=str, help="Name of the project to deploy.")
    parser.add_argument("--PROD", action="store_true", help="Deploy to production server instead of DEV.")
    parser.add_argument("--API", action="store_true", help="Deploy APIs")
    parser.add_argument("--DEV", action="store_true", help="Deploy to Dev environment on web host.")
    parser.add_argument("--CHECK", action="store_true", help="Run file check ONLY to adjust files.")
    parser.add_argument("--SKIP", action="store_true", help="Skip Playwright tests.")
    args = parser.parse_args()
    return args.project, args.PROD, args.API, args.DEV, args.CHECK, args.SKIP

# Loop through potential local paths and create if missing
# IF PROD -> change dir to project root ROOT_BASE + project_name
def setup(name, PROD=False):

    dev_path = Win.join(DEV_BASE,name)
    prod_path = Win.join(PROD_BASE,name)
    wamp_path = Win.join(WAMP_BASE,name)
    api_path = Win.join(API_BASE,name)
    dCache = Win.join(DEV_CACHE,name)
    wCache = Win.join(WAMP_CACHE,name)
    pCache = Win.join(PROD_CACHE,name)
    aCache = Win.join(API_CACHE,name)
    root = Win.join(ROOT_BASE,name)

    for base in [dev_path, prod_path, wamp_path, api_path, dCache, wCache, pCache, aCache]:
        if not Win.exists(base):
            print(f"Creating project directory '{base}'...")
            os.makedirs(base)
    if PROD:
        os.chdir(root)
        print("running playwright tests...")
        subprocess.check_call('npx playwright install', shell=True)
        subprocess.check_call('npx playwright test --retries 2', shell=True)
    else:
        print("skipping playwright...")

    return True

# Check files for any modifications found in mods.json
# Modify the files according to the JSON and add to recycle.json
def check_files(name,PROD=False,DEV=False,CHECK=False):
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

    PATH_BASE = Win.join(ROOT_BASE,name)
    SRC = Win.join(PATH_BASE,"src\\")
    TEMP = Win.join(PATH_BASE,"temp\\")
    MODS = Win.join(PATH_BASE,"mods.json")
    recycling = []
    recycleBin = Win.join(PATH_BASE,"recycling.json")

    if CHECK and PROD:
        print("Checking Production...")
    elif CHECK and DEV:
        print("Checking Development...")
    elif not CHECK:
        print("Proceeding without Check...")
    else:
        print("Oops, missing PROD or DEV, try again with one of those flags.")
        exit(0)

    with open(MODS,"r") as file:
        mods = json.load(file)

    if not os.path.exists(TEMP):
        os.mkdir(TEMP)

    for mod in mods:
        isProd = mod.get("PROD")
        isDev = mod.get("DEV")
        if PROD and not isProd:
            continue
        if DEV and not isDev:
            continue
        
        filename = mod['filename']
        file = Win.join(SRC,filename) #contains full path
        search = mod['search']
        update = mod['update']
        filename = Win.basename(file)
        backup = Win.join(TEMP,filename)
        if CHECK:
            shutil.copyfile(src=file,dst=backup)
            print(f"Original file {file} copied to {backup}")
        contents = ''
        with open(file) as original:
            for line in original:
                newLine = ''
                if line.find(search) != -1:
                    print(f"Found a change in {filename} for {search}")
                    newLine = line.replace(search, update)
                    print(f"Adding {filename} to cleanup")
                    if file not in recycling:
                        recycling.append(file)
                else:
                    newLine = line
                contents += newLine
        with open(file,"w") as original:
            original.write(contents)    
    try:
        with open(recycleBin, "x") as trash:
            json.dump(recycling, trash)
    except FileExistsError:
        print(f"Trash is present, adding to instance...")
        with open(recycleBin, "r") as trash:
            if not recycling:
                recycling = json.load(trash)
            else:
                recycling.append(json.load(trash))
    return recycling

# Loop through recycling, copy files to original location,
# remove files and temp directories, then run 'npm clean' when done
def cleanup(name, recycling=False):

    PATH_BASE = Win.join(ROOT_BASE,name)
    TEMP = Win.join(PATH_BASE, "temp\\")
    recycleBin = Win.join(PATH_BASE,"recycling.json")

    # IF recycling wasn't passed in, look for it
    if not recycling:
        if not Win.exists(recycleBin):
            print(f"Looks like nothing needs cleaned up here... Guess I'll be leaving then.")
            exit(0)
        else:
            with open(recycleBin, "r") as trash:
                trashTmp = json.load(trash)
                try:
                    recycling = trashTmp[0]
                except IndexError:
                    recycling = trashTmp

    for trash in recycling:
        file = Win.split(trash)
        tmpFile = Win.join(TEMP,file[1])
        print(f"Copying temp file: {tmpFile} to origin: {trash}")
        try:
            shutil.copyfile(src=tmpFile,dst=trash)
            os.remove(tmpFile)
        except FileNotFoundError:
            print(f"File {tmpFile} missing, please investigate proceeding with cleanup...")
    try:
        os.rmdir(TEMP)
        os.remove(recycleBin)
    except OSError:
        input("Contents not empty, please verify prior to delete...")
        for f in os.listdir(TEMP):
             os.remove(f)
    except FileNotFoundError:
        print("TMP directory or recycleBin are missing, which is ok.")
    
    os.chdir(PATH_BASE)
    subprocess.check_call('npm run clean', shell=True, cwd=PATH_BASE)    
    print("Cleanup complete")

# Copy all files in project directory to cache location
# Dump old data if present. Only the last push is cached
def cache_files(name, PROD=False, API=False):

    if PROD:
        prod_path = Win.join(PROD_BASE,name)
        pCache = Win.join(PROD_CACHE,name)
        if not Win.exists(prod_path):
            print(f"Production path '{prod_path}' does not exist.")
            print(f"Creating directory '{prod_path}'...")
            os.makedirs(prod_path)
        # Copy files from prod to cache
        for item in os.listdir(prod_path):
            src = Win.join(prod_path, item)
            dest = Win.join(pCache, item)
            try:
                shutil.move(src, dest)
            except Exception as e:
                print(f"Destination '{dest}' present, dumping contents and trying again...")
                shutil.rmtree(dest)
                shutil.move(src, dest)
        print(f"Production Project '{name}' cached successfully from production.")
        return
    
    if API:
        api_path = Win.join(API_BASE,name)
        aCache = Win.join(API_CACHE,name)
        if not Win.exists(api_path):
            print(f"API path '{api_path}' does not exist.")
            print(f"Creating directory '{api_path}'...")
            os.makedirs(api_path)
        # Copy files from api to cache
        for item in os.listdir(api_path):
            src = Win.join(api_path, item)
            dest = Win.join(aCache, item)
            try:
                shutil.move(src, dest)
            except Exception as e:
                print(f"Destination '{dest}' present, dumping contents and trying again...")
                shutil.rmtree(dest)
                shutil.move(src, dest)
        print(f"Production Project '{name}' cached successfully from production.")
        return

    dev_path = Win.join(DEV_BASE,name)
    wamp_path = Win.join(WAMP_BASE,name)

    dCache = Win.join(DEV_CACHE,name)
    wCache = Win.join(WAMP_CACHE,name)


    # Copy files from dev to cache
    for item in os.listdir(dev_path):
        src = Win.join(dev_path, item)
        dest = Win.join(dCache, item)
        try:
            shutil.move(src, dest)
        except Exception as e:
            print(f"Destination '{dest}' present, dumping contents and trying again...")
            shutil.rmtree(dest)
            shutil.move(src, dest)

    # Copy files from wamp to cache
    for item in os.listdir(wamp_path):
        src = Win.join(wamp_path, item)
        dest = Win.join(wCache, item)
        try:
            shutil.move(src, dest)
        except Exception as e:
            print(f"Destination '{dest}' present, dumping contents and trying again...")
            shutil.rmtree(dest)
            shutil.move(src, dest)

    print(f"Project '{name}' cached successfully.")

# Copy all files from build directory to staging location
# IF directory is found, it copies the entire tree down.
def deploy_files(name, PROD=False, API=False):
    
    root = Win.join(ROOT_BASE,name)

    if PROD:
        prod_path = Win.join(PROD_BASE,name)
        build_path = Win.join(root,"\\build\\client\\")

        if not Win.exists(prod_path):
            print(f"Production path '{prod_path}' does not exist.")
            print(f"Creating directory '{prod_path}'...")
            os.makedirs(prod_path)

        # Copy files from build to prod
        for item in os.listdir(build_path):
            src = Win.join(build_path, item)
            dest = Win.join(prod_path, item)
            if Win.isdir(src):
                shutil.copytree(src, dest, dirs_exist_ok=True)
            else:
                shutil.copy2(src, dest)

        print(f"Production Project '{name}' deployed successfully to production.")
        return
    
    if API:
        api_path = Win.join(API_BASE,name)
        build_path = Win.join(root,"\\src\\api\\v1\\")

        if not Win.exists(api_path):
            print(f"API path '{api_path}' does not exist.")
            print(f"Creating directory '{api_path}'...")
            os.makedirs(api_path)

        # Copy files from build to api
        for item in os.listdir(build_path):
            src = Win.join(build_path, item)
            dest = Win.join(api_path, item)

            if Win.isdir(src):
                shutil.copytree(src, dest, dirs_exist_ok=True)
            else:
                shutil.copy2(src, dest)

        print(f"API for Project '{name}' deployed successfully to production.")
        return
    pathBit = "build\\client\\"
    dev_path = Win.join(DEV_BASE,name)
    wamp_path = Win.join(WAMP_BASE,name)
    build_path = Win.join(root,pathBit)

    if not Win.exists(dev_path):
        print(f"Development path '{dev_path}' does not exist.")
        print(f"Creating directory '{dev_path}'...")
        os.makedirs(dev_path)

    if not Win.exists(wamp_path):
        print(f"WAMP path '{wamp_path}' does not exist.")
        print(f"Creating directory '{wamp_path}'...")
        os.makedirs(wamp_path)
        
    # Copy files from build to dev
    for item in os.listdir(Win.abspath(build_path)):
        src = Win.join(build_path, item)
        destDev = Win.join(dev_path, item)
        destWamp = Win.join(wamp_path, item)
        if Win.isdir(src):
            shutil.copytree(src, destDev, dirs_exist_ok=True)
            shutil.copytree(src, destWamp, dirs_exist_ok=True)
        else:
            shutil.copy2(src, destDev)
            shutil.copy2(src, destWamp)

    print(f"Project '{name}' staged successfully.")

def ftp_prod(name, PROD=False, API=False, DEV=False):
    
    root = Win.join(ROOT_BASE,name)

    KEY_PATH = Win.realpath("C:\\Users\\image\\.ssh\\home_ssh")
    prod_path = Win.join(PROD_BASE,name)
    api_path = Win.join(API_BASE,name)
    dev_path = Win.join(DEV_BASE,name)

    if PROD:
        LOCAL_ROOT = prod_path
        location = 'Production'
        if name == "DnD-app":
            REMOTE = DND_REMOTE
        else:
            REMOTE = PROD_REMOTE
    elif API:
        LOCAL_ROOT = api_path
        location = 'API'
        if name == "DnD-app":
            REMOTE = Unx.join(DND_REMOTE,"api/v1/")
        elif DEV:
            REMOTE = Unx.join(DEV_REMOTE,"api/v1/")
        else:
            REMOTE = Unx.join(PROD_REMOTE,"api/v1/")
    elif DEV:
        LOCAL_ROOT = dev_path
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
    def recurse_dir(dir, REMOTE, top):
        for file in dir:
            if Win.isdir(file):
                recurse_dir(file)
            else:
                relPath = Win.relpath(file,top)
                remotePath = Unx.join(REMOTE,relPath)
                print(f"Local: {file} vs Remote: {remotePath}")
                sftp.put( f"{file}", f"{remotePath}" )
                print(f"{file} moved to {remotePath} subdirectory {relPath} successfully" )
    dir = os.scandir( LOCAL_ROOT )
    for file in dir:
        if file.name in ["bucket.php","kothis.DB_make.sql","sylphaxiom.DB_make.sql"]:
            if file.name == "bucket.php":
                continue
            sftp.put(Win.join(path,file.name), Unx.join(API_SECURE,file.name))
            print( f"{file.name} moved to {location} successfully" )
            continue
        if file.is_file():
            sftp.put(file, Unx.join(REMOTE,file.name))
            print(f"{file.name} moved to {location} successfully" )
        if file.is_dir():
            for path, dirs, files in os.walk(file):
                for dir in dirs:
                    try:
                        winPath = Win.join(path,dir)
                        bits = pathlib.PureWindowsPath(winPath).relative_to(LOCAL_ROOT)
                        relPath = pathlib.PurePath.as_posix(pathlib.PureWindowsPath(bits))
                        remotePath = Unx.join(REMOTE,relPath)
                        print(f"Local: {subfile} vs Remote: {remotePath}")
                        sftp.listdir(remotePath)
                    except:
                        print(f"Remote directory {remotePath} is missing, please add directory to continue...")
                        input("Press Enter to continue...")
                for subfile in files:
                    if Win.isdir(subfile):
                        recurse_dir(subfile, REMOTE, path)
                    else:
                        pathlib.PureWindowsPath(root).anchor
                        winPath = Win.join(path,subfile)
                        bits = pathlib.PureWindowsPath(winPath).relative_to(LOCAL_ROOT)
                        relPath = pathlib.PurePath.as_posix(pathlib.PureWindowsPath(bits))
                        remotePath = Unx.join(REMOTE,relPath)
                        print(f"Local: {subfile} vs Remote: {remotePath}")
                        sftp.put( winPath, remotePath )
                        print(f"{subfile} moved to {remotePath} subdirectory {relPath} successfully" )

if __name__ == "__main__":
    import time
    import math
    start = time.time()
    trash = ''
    [project_name, PROD, API, DEV, CHECK, SKIP] = parse_args()
    if setup(project_name, PROD=PROD):
        if (CHECK):
            check_files(project_name, PROD=PROD, DEV=DEV, CHECK=CHECK)
            print("I'm out, see you after the build is done.")
            exit(0)
        cache_files(project_name, PROD=PROD, API=API)
        deploy_files(project_name, PROD=PROD, API=API)
        if (PROD and not CHECK):
            trash = check_files(project_name, PROD=PROD)
            ftp_prod(project_name, PROD=PROD)
        if (API):
            ftp_prod(project_name, API=API)
        if (DEV and not CHECK):
            trash = check_files(project_name, DEV=DEV)
            ftp_prod(project_name, DEV=DEV)
    else:
        print("Directory check failed. Deployment aborted.")
    cleanup(project_name,recycling=trash) #Cleanup no matter what :)
    end = time.time()
    duration = math.floor(end-start)
    print(f"Deployment completed in {duration}s.")