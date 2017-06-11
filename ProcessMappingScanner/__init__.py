# Copyright (c) 2015, 2016, 2017 Tim Savannah under terms of the Lesser General GNU Public License Version 3 ( LGPLv3 )
# You should have received a copy of the license as LICENSE with this distribution. It contains the full license
#
# This module contains methods designed to work under UNIX to determine various information associated with processes.
# The include shared mappings (like shared lib, running executable, etc), process owner, process commandline, and open files, devices, or fds.

# vim: set ts=4 sw=4 expandtab


import os
import pwd
import sys

try:
    FileNotFoundError
except:
    FileNotFoundError = IOError
    PermissionError = IOError

__version__ = '2.2.1'
__version_tuple__ = (2, 2, 1)

__all__ = ("getProcessOwner", "getProcessOwnerStr", "getProcessCommandLineStr", "getProcessCommandLineList", "getProcessCwd", "getAllRunningPids", "scanProcessForMapping", "scanAllProcessesForMapping", "scanProcessForOpenFile", "scanAllProcessesForOpenFile" )

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


def getProcessCwd(pid):
    '''
        getProcessCwd - Gets the cwd (current working directory) of a given pid

        @param pid <int> - Process ID

        @return <str/None> - None if process not found or can't be determined. Otherwise, a string of the CWD
    '''
    try:
        cwd = os.readlink('/proc/%d/cwd' %(int(pid), ))

        return cwd
    except:
        return None
        

def getAllRunningPids():
    '''
        getAllRunningPids - Gets list of all pids that are running on a given system

        @return <list<int>> - A list of pids (process IDs).
    '''
    return [int(x) for x in os.listdir('/proc') if x.isdigit()]

        
def scanProcessForMapping(pid, searchPortion, isExactMatch=False, ignoreCase=False):
    '''
        scanProcessForMapping - Searches a given pid's mappings for a certain pattern.

            @param pid <int> - A running process ID on this system
            @param searchPortion <str> - A mapping for which to search, example: libc or python or libz.so.1. Give empty string to return all mappings.
            @param isExactMatch <bool> Default False - If match should be exact, otherwise a partial match is performed.
            @param ignoreCase <bool> Default False - If True, search will be performed case-insensitively

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

            if ignoreCase is False:
                isMatch = lambda searchFor, searchIn : bool(searchFor == searchIn)
            else:
                isMatch = lambda searchFor, searchIn : bool(searchFor.lower() == searchIn.lower())
        else:
            if ignoreCase is False:
                isMatch = lambda searchFor, searchIn : bool(searchFor in searchIn)
            else:
                isMatch = lambda searchFor, searchIn : bool(searchFor.lower() in searchIn.lower())
                

        for line in lines:
            portion = ' '.join(line.split(' ')[5:]).lstrip()
            if isMatch(searchPortion, portion):
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


def scanAllProcessesForMapping(searchPortion, isExactMatch=False, ignoreCase=False):
    '''
        scanAllProcessesForMapping - Scans all processes on the system for a given search pattern.

            @param searchPortion <str> - A mapping for which to search, example: libc or python or libz.so.1. Give empty string to return all mappings.
            @param isExactMatch <bool> Default False - If match should be exact, otherwise a partial match is performed.
            @param ignoreCase <bool> Default False - If True, search will be performed case-insensitively

        @return - <dict> - A dictionary of pid -> mappingResults for each pid that matched the search pattern. For format of "mappingResults", @see scanProcessForMapping
    '''
    pids = getAllRunningPids()

    # Since processes could disappear, we run the scan as fast as possible here with a list comprehension, then assemble the return dictionary later.
    mappingResults = [scanProcessForMapping(pid, searchPortion, isExactMatch, ignoreCase) for pid in pids]
    ret = {}
    for i in range(len(pids)):
        if mappingResults[i] is not None:
            ret[pids[i]] = mappingResults[i]

    return ret

#  REMOVED in 2.1.0 - Uncomment to restore typo compat.
# scanAllProcessessForMapping = scanAllProcessesForMapping # Backwards compat with typo, will be kept for one release.       


def scanProcessForOpenFile(pid, searchPortion, isExactMatch=True, ignoreCase=False):
    '''
        scanProcessForOpenFile - Scans open FDs for a given pid to see if any are the provided searchPortion

            @param searchPortion <str> - Filename to check
            @param isExactMatch <bool> Default True - If match should be exact, otherwise a partial match is performed.
            @param ignoreCase <bool> Default False - If True, search will be performed case-insensitively

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

            if ignoreCase is False:
                isMatch = lambda searchFor, totalPath : bool(searchFor == totalPath)
            else:
                isMatch = lambda searchFor, totalPath : bool(searchFor.lower() == totalPath.lower())
        else:
            if ignoreCase is False:
                isMatch = lambda searchFor, totalPath : bool(searchFor in totalPath)
            else:
                isMatch = lambda searchFor, totalPath : bool(searchFor.lower() in totalPath.lower())
            

        for fd in processFDs:
            fdPath = os.readlink(prefixDir + '/' + fd)

            if isMatch(searchPortion, fdPath):
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


def scanAllProcessesForOpenFile(searchPortion, isExactMatch=True, ignoreCase=False):
    '''
        scanAllProcessessForOpenFile - Scans all processes on the system for a given filename

            @param searchPortion <str> - Filename to check
            @param isExactMatch <bool> Default True - If match should be exact, otherwise a partial match is performed.
            @param ignoreCase <bool> Default False - If True, search will be performed case-insensitively

        @return - <dict> - A dictionary of pid -> mappingResults for each pid that matched the search pattern. For format of "mappingResults", @see scanProcessForOpenFile
    '''
    pids = getAllRunningPids()

    # Since processes could disappear, we run the scan as fast as possible here with a list comprehension, then assemble the return dictionary later.
    mappingResults = [scanProcessForOpenFile(pid, searchPortion, isExactMatch, ignoreCase) for pid in pids]
    ret = {}
    for i in range(len(pids)):
        if mappingResults[i] is not None:
            ret[pids[i]] = mappingResults[i]

    return ret


