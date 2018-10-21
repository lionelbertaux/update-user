## Python script to udpate a linux user profile with custom preferences
# Updates the files contained in the JSON in file-list. Required fiels:
# file: name of the file in the folder
# path: path to replace with its path + name


from os.path import expanduser
import json
import os

# Static configuration
fileJSON = "file-list"


def readBashAliases(fPath):
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


# Configuration / Variable collection
homeDir = expanduser("~")
with open(fileJSON) as json_data:
    fileList = json.load(json_data)

print("Home directory of user is: " + homeDir)
for cFile in fileList:
    print("Updating " + cFile['path'] + " with content of " + cFile["file"])
    # read current configuration file
    fullPath = homeDir + os.sep + cFile['path']
    # bash aliases, try to decode the file and stire in dict
    if cFile['file'] == "bash_aliases":
        # print("---------------------")
        current_file = readBashAliases(fPath=fullPath)
        # print(current_file)
        # print("---------------------")
        new_file = readBashAliases(fPath=cFile['file'])
        # print(new_file)
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
        # print(updated_file)
        # Now print the new file
        f = open(fullPath+str("tmp"), "w")
        for topic,value in updated_file.items():
            # search for the same alias key
            f.write("\n##"+topic + "\n")
            for short, cmd in value.items():
                # f.write("alias " + str(short) + ":" + str(cmd) + "\n")
                f.write(str(cmd)+"\n")
        f.close()
