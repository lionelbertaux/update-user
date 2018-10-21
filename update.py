## Author: Lionel Bertaux
## Date: 21-10-2018
## Python script to udpate a linux user profile with custom preferences

from os.path import expanduser
from shutil import copyfile

import datetime
import json
import os
import argparse


# Static configuration
fileJSON = "file-list"


def saveFile(fPath):
    if os.path.exists(fPath):
        # generate a copy of the current config file
        today = str(datetime.datetime.now()).split(".")[0].replace(":","").replace("-","").replace(" ", "-")
        copyfile(fPath, fPath+str("_")+str(today))


def readBashAliases(fPath):
    # Read bash_aliases file and return the content in a dict
    # Lines starting with a '##' are interpreted as a topic
    # Comments ('#') are copied as well
    with open(fPath) as f:
        lines = f.readlines()
    lines = [x.strip() for x in lines]
    lines_dict = {}
    topic = "various"
    for line in lines:
        # Check if this is an alias or not
        if not 'alias ' == line[:6]:
            if "##" == line[:2]:
                # Change topic
                topic = line.replace("##", "")
                continue
        # remove the alias part and split key and value
        # line = line.replace("alias ", "")
        # line_split = line.split("=")
        # only keep real alias lines or comments
        if  len(line)<=1  or (line[0] != '#' and (len(line.split("="))<=1 or 'alias ' != line[:6])):
            continue
        if not topic in lines_dict.keys():
            lines_dict.update({topic:{}})
        # lines_dict[topic].update({line_split[0] : '='.join(line_split[1:]) })
        lines_dict[topic].update({line.split("=")[0]: line })
    return lines_dict


def updateFiles(homeDir, fileList):
    # update files contained in list
    # Smart update for bash_aliases
    # Simple copy for others
    for cFile in fileList:
        print("Updating " + cFile['path'] + " with content of " + cFile["file"])
        # read current configuration file
        fullPath = homeDir + os.sep + cFile['path']
        # bash aliases, try to decode the file and stire in dict
        if cFile['file'] == "bash_aliases":
            new_file = readBashAliases(fPath=cFile['file'])
            if os.path.exists(fullPath):
                current_file = readBashAliases(fPath=fullPath)
            else:
                current_file = {}
            updated_file = {}
            [ updated_file.update({k: v}) for k,v in current_file.items()]
            # Now compare both files
            for topic,value in new_file.items():
                # search for the same alias key
                for short, cmd in value.items():
                    matches = [ k for val in current_file.values() for k,v in val.items() if short == k]
                    # for val in current_file.values():
                    #     for k,v in val.items():
                    #         print(str(k) + ": " +str(v) )
                    if len(matches) == 1:
                        continue
                    else:
                        # Add the values to the updated file
                        if topic in updated_file.keys():
                            updated_file[topic].update({short: cmd})
                        else:
                            updated_file.update({topic: {short: cmd}})
            # Save current file
            saveFile(fullPath)
            # Now print the new file
            f = open(fullPath, "w")
            for topic,value in updated_file.items():
                # search for the same alias key
                f.write("\n##"+topic + "\n")
                for short, cmd in value.items():
                    # f.write("alias " + str(short) + ":" + str(cmd) + "\n")
                    f.write(str(cmd)+"\n")
            f.close()
        else:
            # for other files, simply save the current config and copy the new one (no smart update)
            saveFile(fullPath)
            copyfile(cFile['file'], fullPath)


def cleanFiles(homeDir, fileList):
    for cFile in fileList:
        print("Cleaning " + cFile['path'] + "_datetime files.")
        # List similar files in the repertory
        fullPath = homeDir + os.sep + cFile['path']
        path_split = os.path.split(fullPath)
        files = os.listdir(path_split[0])
        for f in files:
            if path_split[1] in f and len(f) > len(path_split[1]):
                print("Removing file " + os.path.join(path_split[0], f))
                os.remove(os.path.join(path_split[0], f))


parser = argparse.ArgumentParser(description="Process cli arguments.")
parser.add_argument("--mode", dest="mode", action="store")
args = parser.parse_args()

# Configuration / Variable collection
homeDir = expanduser("~")
with open(fileJSON) as json_data:
    fileList = json.load(json_data)
print("Home directory of user is: " + homeDir)
if args.mode:
    if args.mode == "update":
        updateFiles(homeDir=homeDir, fileList=fileList)
    elif args.mode == "clean":
        cleanFiles(homeDir=homeDir, fileList=fileList)
    else:
        print("Invalid mode. Available: 'update'.")


