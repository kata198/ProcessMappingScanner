# Copyright (c) 2015 Tim Savannah under terms of the Lesser General GNU Public License Version 3 ( LGPLv3 )
# You should have received a copy of the license as LICENSE with this distribution. It contains the full license
#
# This module contains methods designed to work under UNIX to determine various information associated with processes.
# The include shared mappings (like shared lib, running executable, etc), process owner, process commandline, and open files, devices, or fds.

# vim: set ts=4 sw=4 expandtab


import os
import time
import traceback
import getpass
import pwd
import sys

try:
    FileNotFoundError
except:
    FileNotFoundError = IOError
    PermissionError = IOError

__version__ = '2.0.1'
__version_tuple__ = (2, 0, 1)

def getProcessOwner(pid):
    '''
        getProcessOwner - Get the process owner of a pid

        @param pid <int> - process id

        @return - None if process not found or can't be determined. Otherwise, a dict: 
            {
                uid  - Owner UID
                name - Owner name, or None if one cannot be determined
            }
    '''
    try:
        ownerUid = os.stat('/proc/' + str(pid)).st_uid
    except:
        return None
    
    try:
        ownerName = pwd.getpwuid(ownerUid).pw_name
    except:
        ownerName = None

    return {
        'uid' : ownerUid,
        'name' : ownerName
    }

def getProcessOwnerStr(pid):
    '''
        getProcessOwner - Get Process owner of a pid as a string instead of components (#getProcessOwner)

        @return - Returns username if it can be determined, otherwise uid, otherwise "unknown"
    '''
    ownerInfo = getProcessOwner(pid)
    if ownerInfo:
        if ownerInfo['name']:
            owner = ownerInfo['name']
        else:
            owner = str(ownerInfo['uid'])
    else:
        owner = 'unknown'

    return owner

def getProcessCommandLineStr(pid):
    '''
        getProcessCommandLineStr - Gets a the commandline (program + arguments) of a given pid

        @param pid <int> - Process ID

        @return - None if process not found or can't be determined. Otherwise a string of commandline.

        @note Caution, args may have spaces in them, and you cannot surmise from this method. If you care (like trying to replay a command), use getProcessCommandLineList instead
    '''
    try:
        with open('/proc/%d/cmdline' %(int(pid),), 'r') as f:
            cmdline = f.read()
        return cmdline.replace('\x00', ' ')
    except:
        return None


def getProcessCommandLineList(pid):
    '''
        getProcessCommandLineList - Gets the commandline (program + argumentS) of a given pid as a list.

        @param pid <int> - Process ID

        @return - None if process not found or can't be determined. Otherwise a list representing argv. First argument is process name, remainder are arguments.

        @note - Use this if you care about whether a process had a space in the commands
    '''
    try:
        with open('/proc/%d/cmdline' %(int(pid),), 'r') as f:
            cmdline = f.read()

        return cmdline.split('\x00')
    except:
        return None


def getAllRunningPids():
    return [int(x) for x in os.listdir('/proc') if x.isdigit()]

        
def scanProcessForMapping(pid, searchPortion, isExactMatch=False):
    '''
        scanProcessForMapping - Searches a given pid's mappings for a certain pattern.

            @param pid <int> - A running process ID on this system
            @param searchPortion <str> - A mapping for which to search, example: libc or python or libz.so.1. Give empty string to return all mappings.
            @param isExactMatch <bool> - If match should be exact, otherwise a partial match is performed. Default False.

            @return <dict> - If result is found, the following dict is returned. If no match found on the given pid, or pid is not found running, None is returned.
                {
                    'searchPortion' : The passed search pattern
                    'pid'           : The passed pid (as an integer)
                    'owner'         : String of process owner, or uid if no mapping can be found, or "unknown" if neither could be determined.
                    'cmdline'       : Commandline string
                    'matchedMappings' : All mappings likes that matched the given search pattern
                }

    '''
    try:   
        try:
            pid = int(pid)
        except ValueError as e:
            sys.stderr.write('Expected an integer, got %s for pid.\n' %(str(type(pid)),))
            raise e
            
        with open('/proc/%d/maps' %(pid,), 'r') as f:
            contents = f.read()

        lines = contents.split('\n')
        matchedMappings = []
    
        if isExactMatch is True:
            for line in lines:
                portion = ' '.join(line.split(' ')[5:]).lstrip()
                if searchPortion == portion:
                    matchedMappings.append('\t' + line)
        else:
            for line in lines:
                if searchPortion in line:
                    matchedMappings.append('\t' + line)


        if len(matchedMappings) == 0:
            return None


        cmdline = getProcessCommandLineStr(pid)
        owner   = getProcessOwnerStr(pid)

        return {
            'searchPortion' : searchPortion,
            'pid'           : pid,
            'owner'         : owner,
            'cmdline'       : cmdline,
            'matchedMappings' : matchedMappings,
        }
    except OSError:
        return None
    except IOError:
        return None
    except FileNotFoundError:
        return None
    except PermissionError:
        return None


def scanAllProcessesForMapping(searchPortion, isExactMatch=False):
    '''
        scanAllProcessesForMapping - Scans all processes on the system for a given search pattern.

            @param searchPortion <str> - A mapping for which to search, example: libc or python or libz.so.1. Give empty string to return all mappings.
            @param isExactMatch <bool> - If match should be exact, otherwise a partial match is performed.

        @return - <dict> - A dictionary of pid -> mappingResults for each pid that matched the search pattern. For format of "mappingResults", @see scanProcessForMapping
    '''
    pids = getAllRunningPids()

    # Since processes could disappear, we run the scan as fast as possible here with a list comprehension, then assemble the return dictionary later.
    mappingResults = [scanProcessForMapping(pid, searchPortion, isExactMatch) for pid in pids]
    ret = {}
    for i in range(len(pids)):
        if mappingResults[i] is not None:
            ret[pids[i]] = mappingResults[i]

    return ret

scanAllProcessessForMapping = scanAllProcessesForMapping # Backwards compat with typo, will be kept for one release.       


def scanProcessForOpenFile(pid, searchPortion, isExactMatch=True):
    '''
        scanProcessForOpenFile - Scans open FDs for a given pid to see if any are the provided searchPortion

            @param searchPortion <str> - Filename to check
            @param isExactMatch <bool> - If match should be exact, otherwise a partial match is performed. Default True.

        @return -  If result is found, the following dict is returned. If no match found on the given pid, or the pid is not found running, None is returned.
                {
                    'searchPortion' : The search portion provided
                    'pid'           : The passed pid (as an integer)
                    'owner'         : String of process owner, or "unknown" if one could not be determined
                    'cmdline'       : Commandline string
                    'fds'           : List of file descriptors assigned to this file (could be mapped several times)
                    'filenames'     : List of the filenames matched
                }
    '''
    try:
        try:
            pid = int(pid)
        except ValueError as e:
            sys.stderr.write('Expected an integer, got %s for pid.\n' %(str(type(pid)),))
            raise e

        prefixDir = "/proc/%d/fd" % (pid,)

        processFDs = os.listdir(prefixDir)

        matchedFDs = []
        matchedFilenames = []

        if isExactMatch is True:
            for fd in processFDs:
                fdPath = os.readlink(prefixDir + '/' + fd)
                if searchPortion == fdPath:
                    matchedFDs.append(fd)
                    matchedFilenames.append(fdPath)
        else:
            for fd in processFDs:
                fdPath = os.readlink(prefixDir + '/' + fd)
                if searchPortion in fdPath:
                    matchedFDs.append(fd)
                    matchedFilenames.append(fdPath)

        if len(matchedFDs) == 0:
            return None

        cmdline = getProcessCommandLineStr(pid)
        owner   = getProcessOwnerStr(pid)
            
        return {
            'searchPortion' : searchPortion,
            'pid'           : pid,
            'owner'         : owner,
            'cmdline'       : cmdline,
            'fds'           : matchedFDs,
            'filenames'     : matchedFilenames, 
        }



    except OSError:
        return None
    except IOError:
        return None
    except FileNotFoundError:
        return None
    except PermissionError:
        return None


def scanAllProcessesForOpenFile(searchPortion, isExactMatch=True):
    '''
        scanAllProcessessForOpenFile - Scans all processes on the system for a given filename

            @param searchPortion <str> - Filename to check
            @param isExactMatch <bool> - If match should be exact, otherwise a partial match is performed. Default True.

        @return - <dict> - A dictionary of pid -> mappingResults for each pid that matched the search pattern. For format of "mappingResults", @see scanProcessForOpenFile
    '''
    pids = getAllRunningPids()

    # Since processes could disappear, we run the scan as fast as possible here with a list comprehension, then assemble the return dictionary later.
    mappingResults = [scanProcessForOpenFile(pid, searchPortion, isExactMatch) for pid in pids]
    ret = {}
    for i in range(len(pids)):
        if mappingResults[i] is not None:
            ret[pids[i]] = mappingResults[i]

    return ret


