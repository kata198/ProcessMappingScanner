# Copyright (c) 2015 Tim Savannah under terms of the Lesser General GNU Public License Version 3 ( LGPLv3 )
# You should have received a copy of the license as LICENSE with this distribution. It contains the full license
#
# This module contains methods designed to work under UNIX to determine mappings used by processes. These could 
#  include the running executable, a shared library, mapped locale file, or something else.

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

def scanProcessForMapping(pid, searchPortion):
    '''
        scanProcessForMapping - Searches a given pid's mappings for a certain pattern.

            @param pid <int> - A running process ID on this system
            @param searchPortion <str> - A mapping for which to search, example: libc or python or libz.so.1. Give empty string to return all mappings.

            @return <dict> - If result is found, the following dict is return. If no match found on the given pid, or pid is not found running, None is returned.
                {
                    'searchPortion' : The passed search pattern
                    'pid'           : The passed pid (as an integer)
                    'owner'         : String of owner, or "unknown" if one could not be determined
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
        for line in lines:
            if searchPortion in line:
                matchedMappings.append('\t' + line)
        if len(matchedMappings) == 0:
            return None

        with open('/proc/%s/cmdline' %(pid,), 'r') as f:
            cmdline = f.read().replace('\x00', ' ')

        try:
            ownerUid = os.stat('/proc/' + str(pid)).st_uid
            owner = pwd.getpwuid(ownerUid).pw_name
        except:
            owner = 'unknown'


        return {
            'searchPortion' : searchPortion,
            'pid'           : pid,
            'owner'         : owner,
            'cmdline'       : cmdline,
            'matchedMappings' : matchedMappings,
        }
    except FileNotFoundError:
        return None
    except PermissionError:
        return None


def scanAllProcessessForMapping(searchPortion):
    '''
        scanAllProcessessForMapping - Scans all processes on the system for a given search pattern.

        @return - <dict> - A dictionary of pid -> mappingResults for each pid that matched the search pattern. For format of "mappingResults", @see scanProcessForMapping
    '''
    pids = [int(x) for x in os.listdir('/proc') if x.isdigit()]

    # Since processes could disappear, we run the scan as fast as possible here with a list comprehension, then assemble the return dictionary later.
    mappingResults = [scanProcessForMapping(pid, searchPortion) for pid in pids]
    ret = {}
    for i in range(len(pids)):
        if mappingResults[i] is not None:
            ret[pids[i]] = mappingResults[i]

    return ret
            

