# Pinewood Builders Automatic Handbook Merge
# By femou

import requests
import subprocess
import time
import random
import os

run_number = 0
while True:
    pbst_changed = False
    tms_changed = False
    pet_changed = False
    pb_changed = False
    run_number += 1
    changecount = 0
    print(f"\nStarting run number {run_number}")
    latestpbst_data = requests.get('https://devforum.roblox.com/raw/2130825')
    print("Saved PBST data")
    #time.sleep(5)
    latestpet_data = requests.get('https://devforum.roblox.com/raw/2130240')
    print("Saved PET data")
    #time.sleep(5)
    latesttms_data = requests.get('https://devforum.roblox.com/raw/595758')
    print("Saved TMS data")
    #time.sleep(5)
    latestpb_data = requests.get('https://devforum.roblox.com/raw/907637')
    print("Saved PB data")

    currentpbst_path = 'pbst_handbook.md'
    currentpet_path = 'pet_handbook.md'
    currenttms_path = 'tms_handbook.md'
    currentpb_path = 'pb_gamerules.md'

    with open(currentpbst_path, "rb+") as f:
        currentpbst = f.read()
    with open(currentpet_path, "rb+") as f:
        currentpet = f.read()
    with open(currenttms_path, "rb+") as f:
        currenttms = f.read()
    with open(currentpb_path, "rb+") as f:
        currentpb = f.read()

    random_id = random.randrange(10000000000001)

    #print(f'Run ID {random_id}')

    latestpbst_path = f'updatefiles/{random_id}_pbst.md'
    latestpet_path = f'updatefiles/{random_id}_pet.md'
    latesttms_path = f'updatefiles/{random_id}_tms.md'
    latestpb_path = f'updatefiles/{random_id}_pb.md'

    with open(latestpbst_path, "ab+") as f:
        f.write(latestpbst_data.content)
    with open(latestpet_path, "ab+") as f:
        f.write(latestpet_data.content)
    with open(latesttms_path, "ab+") as f:
        f.write(latesttms_data.content)
    with open(latestpb_path, "ab+") as f:
        f.write(latestpb_data.content)

    with open("error_files/502.md", "rb+") as f:
        error502 = f.read()
    with open("error_files/blank.md", "rb+") as f:
        errorblank = f.read()
    with open("error_files/504.md", "rb+") as f:
        error504 = f.read()
    

    if latestpbst_data.content == errorblank:
        print("PBST data returned blank, skipping")
        os.remove(latestpbst_path)
    elif latestpbst_data.content == error502:
        print("PBST data returned a 502, skipping")
        os.remove(latestpbst_path)
    elif latestpbst_data.content.startswith(b'<html'):
        print("PBST data returned a DevForum error, skipping")
        os.remove(latestpbst_path)
    elif latestpbst_data.content == error504:
        print("PBST data returned a 504, skipping")
        os.remove(latestpbst_path)
    elif latestpbst_data.content != currentpbst:
        with open(currentpbst_path, "wb") as f:
            f.write(latestpbst_data.content)
        print(f"Update to PBST handbook applied with ID {random_id}")
        subprocess.run(["git", "add", currentpbst_path])
        changecount += 1
        pbst_changed = True
    else:
        os.remove(latestpbst_path)
        print("No changes for PBST")

    if latestpet_data.content == errorblank:
        print("PET data returned blank, skipping")
    elif latestpet_data.content == error502:
        print("PET data returned a 502, skipping")
    elif latestpet_data.content.startswith(b'<html'):
        print("PET data returned a DevForum error, skipping")
    elif latestpet_data.content == error504:
        print("PET data returned a 504, skipping")
    elif latestpet_data.content != currentpet:
        with open(currentpet_path, "wb") as f:
            f.write(latestpet_data.content)
        print(f"Update to PET handbook applied with ID {random_id}")
        subprocess.run(["git", "add", currentpet_path])
        changecount += 1
        pet_changed = True
    else:
        os.remove(latestpet_path)
        print("No changes for PET")

    if latesttms_data.content == errorblank:
        print("TMS data returned blank, skipping")
    elif latesttms_data.content == error502:
        print("TMS data returned a 502, skipping")
    elif latesttms_data.content.startswith(b'<html'):
        print("TMS data returned a DevForum error, skipping")
    elif latesttms_data.content == error504:
        print("TMS data returned a 504, skipping")
    elif latesttms_data.content != currenttms:
        with open(currenttms_path, "wb") as f:
            f.write(latesttms_data.content)
        print(f"Update to TMS handbook applied with ID {random_id}")
        subprocess.run(["git", "add", currenttms_path])
        changecount += 1
        tms_changed = True
    else:
        os.remove(latesttms_path)
        print("No changes for TMS")

    if latestpb_data.content == errorblank:
        print("PB data returned blank, skipping")
    elif latestpb_data.content == error502:
        print("PB data returned a 502, skipping")
    elif latestpb_data.content.startswith(b'<html'):
        print("PB data returned a DevForum error, skipping")
    elif latestpb_data.content == error504:
        print("PB data returned a 504, skipping")
    elif latestpb_data.content != currentpb:
        with open(currentpb_path, "wb") as f:
            f.write(latestpb_data.content)
        print(f"Update to PB game rules applied with ID {random_id}")
        subprocess.run(["git", "add", currentpb_path])
        changecount += 1
        pb_changed = True
    else:
        os.remove(latestpb_path)
        print("No changes for PB")

    if changecount > 0:
        git_message = "Handbook update for "
        if pbst_changed == True:
            git_message += "PBST, "
        if tms_changed == True:
            git_message += "TMS, "
        if pet_changed == True:
            git_message += "PET, "
        if pb_changed == True:
            git_message += "PB, "
        
        git_message = git_message.rpartition(", ")[0]
        if changecount == 1:
            print("Pushing 1 file to Github")
        else:
            print(f"Pushing {changecount} files to Github")
        subprocess.run(["git", "commit", "-m", git_message])
        subprocess.run(["git", "push"])
        print("Push complete")
    else: 
        print("None of the handbooks have changed, skipping git")

    print(f"Run number {run_number} complete")
    time.sleep(885)