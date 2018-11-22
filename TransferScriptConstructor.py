import os
import sys
from stat import S_IEXEC


scriptFileFullPath = ""
hostsFileFullPath = ""
remoteUserName = ""
fromLocalToRemote = False
fromRemoteToLocal = False
localDir = ""
remoteDir = ""
generalFileName = ""
isFileWithNum = False


def parseArgs(mainArgs):

    if len(mainArgs) > 17:  #It gets to 17 as there is also the program's name
        raise Exception("\"makeTransferScript\" expected only up to 16 arguments, while you gave: " + len(mainArgs).__str__() + "!")

    i = 1
    while i < len(mainArgs):

        # print i.__str__() + ". outer-arg: " + mainArgs[i]  # DEBUG!

        if mainArgs[i] == "-scriptFileFullPath":
            i += 1
            # print i.__str__() + ". inner-arg: " + mainArgs[i]  # DEBUG!
            global scriptFileFullPath
            scriptFileFullPath = mainArgs[i]
        elif mainArgs[i] == "-hostsFileFullPath":
            i += 1
            # print i.__str__() + ". inner-arg: " + mainArgs[i]  # DEBUG!
            global hostsFileFullPath
            hostsFileFullPath = mainArgs[i]
        elif mainArgs[i] == "-remoteUserName":
            i += 1
            # print i.__str__() + ". inner-arg: " + mainArgs[i]  # DEBUG!
            global remoteUserName
            remoteUserName = mainArgs[i]
        elif mainArgs[i] == "--wayOfTransfer":
            i += 1
            # print i.__str__() + ". inner-arg: " + mainArgs[i]  # DEBUG!
            global fromLocalToRemote
            if mainArgs[i] == "-fromLocalToRemote":
                fromLocalToRemote = True
            elif mainArgs[i] == "-fromRemoteToLocal":
                fromRemoteToLocal = True
            else:
                raise Exception('"--fromLocalToRemote" was followed by the invalid argument: "' + mainArgs[i] + '" the expected one was: \"-True/False\"')
        elif mainArgs[i] == "-localDir":
            i += 1
            # print i.__str__() + ". inner-arg: " + mainArgs[i]  # DEBUG!
            global localDir
            localDir = mainArgs[i]
        elif mainArgs[i] == "-remoteDir":
            i += 1
            # print i.__str__() + ". inner-arg: " + mainArgs[i]  # DEBUG!
            global remoteDir
            remoteDir = mainArgs[i]
        elif mainArgs[i] == "-generalFileName":
            i += 1
            # print i.__str__() + ". inner-arg: " + mainArgs[i]  # DEBUG!
            global generalFileName
            generalFileName = mainArgs[i]
        elif mainArgs[i] == "--isFileWithNum":
            i += 1
            # print i.__str__() + ". inner-arg: " + mainArgs[i]  # DEBUG!
            global isFileWithNum
            if mainArgs[i] == "-True":
                isFileWithNum = True
            elif mainArgs[i] == "-False":
                isFileWithNum = False
            else:
                raise Exception('"--isFileWithNums" was followed by the invalid argument: "' + mainArgs[i] + '" the expected one was: \"-True/False\"')
        else:
            raise Exception("Unexpected argument found: " + mainArgs[i])

        i += 1


hosts = []


def loadHosts():
    f = open(hostsFileFullPath, "r")
    global hosts
    hosts = f.read().splitlines()
    # print hosts
    f.close()


fileToTransfer = ""
preNumStatement = ""
afterNumStatement = ""
statementAfterHost = ""
command = "scp"     # const
statementBeforeHost = ""

def constructBasicCommandComponents():

    global preNumStatement, afterNumStatement, statementBeforeHost, statementAfterHost, localDir

    # split "generalFileName" in pre-extension and after-extension which parts will be used later if we have files with numbers.
    generalFileNameInPieces = generalFileName.split(".")

    if len(generalFileNameInPieces) != 2:
        raise Exception("Tried to split the generalFileName: \"" + generalFileName + "\" but gave " + len(generalFileNameInPieces).__str__() + " part(s).")

    preNumStatement = generalFileNameInPieces[0]
    afterNumStatement = "." + generalFileNameInPieces[1]

    #If we are transferring fromRemoteToLocal, then is possible that the localDir doesn't exist, so we need to create it.
    if fromRemoteToLocal:
        if not os.path.isdir(localDir):
            os.makedirs(localDir)

    localDir = " " + localDir
    statementBeforeHost = " " + remoteUserName + "@"
    statementAfterHost = ":" + remoteDir


def finalCmdConstructAndWriteToTransferScript():

    global fileToTransfer

    f = open(scriptFileFullPath, "w+")

    localFullPath = ""
    remoteFullPath = ""

    if not isFileWithNum:   # Avoid running solid-statements multiple times inside the loop
        fileToTransfer = preNumStatement + afterNumStatement
        localFullPath = os.path.join(localDir, fileToTransfer)
        remoteFullPath = os.path.join(statementAfterHost, fileToTransfer)

    for i in range(0, len(hosts)):

        if isFileWithNum:
            fileToTransfer = preNumStatement + (i+1).__str__() + afterNumStatement
            localFullPath = os.path.join(localDir, fileToTransfer)
            remoteFullPath = os.path.join(statementAfterHost, fileToTransfer)

        if fromLocalToRemote:
            transferCmd = command + localFullPath + statementBeforeHost + hosts[i] + statementAfterHost
        else:
            transferCmd = command + statementBeforeHost + hosts[i] + remoteFullPath + localDir

        print(transferCmd)

        f.write(transferCmd + "\n")

    f.close()


def constructTransferScript():

    parseArgs(sys.argv)

    loadHosts()

    constructBasicCommandComponents()

    print "\nConstructing transfer-script: \"" + scriptFileFullPath + "\"..\n"

    finalCmdConstructAndWriteToTransferScript()

    print "\nConstruction finished."
    print "Run transfer-script: \"" + scriptFileFullPath + "\""

    # Give the necessary permissions to the transferScript.
    os.chmod(scriptFileFullPath, S_IEXEC | os.stat(scriptFileFullPath).st_mode)


if __name__ == '__main__':
    constructTransferScript()
