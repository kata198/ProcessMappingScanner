ProcessMappingScanner
=====================

Python module for scanning running processes for various pieces of information ( mappings, open files, owner, commandline, etc )

This module works on UNIX-derived systems only (Linux, BSD, cygwin, etc)


**What is a mapping?**


A mapping can include the running executable (like python), a shared library (like libc) or something else (like a locale-archive file or other mapping).

You can use this module to, for example, scan for running processes to see what is using libpython2.7, or scan a paticular process for a mapping.


Commandline Tool
----------------

ProcessMappingScanner's functionality is exposed through a commandline tool, `findProcessesUsing <https://github.com/kata198/findProcessesUsing>`_.



Functions
---------


**Mappings**


Here are functions to scan running processes for mappings.


The following function, scanProcessForMapping, scans a single process for mappings. Use an empty string for searchPortion to get all mappings.

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


The following function, scanAllProcessesForMapping, scans all running processes for mappings.

	def scanAllProcessesForMapping(searchPortion, isExactMatch=False, ignoreCase=False):

		'''

			scanAllProcessesForMapping - Scans all processes on the system for a given search pattern.


				@param searchPortion <str> - A mapping for which to search, example: libc or python or libz.so.1. Give empty string to return all mappings.

				@param isExactMatch <bool> Default False - If match should be exact, otherwise a partial match is performed.

				@param ignoreCase <bool> Default False - If True, search will be performed case-insensitively


			@return - <dict> - A dictionary of pid -> mappingResults for each pid that matched the search pattern. For format of "mappingResults", @see scanProcessForMapping

		'''


**Owner**


Here are the functions to determine whom is running a process


The following function returns information on the owner of a given process (uid, username):

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


The following functions returns a string of the owner of a given process:

	def getProcessOwnerStr(pid):

		'''

			getProcessOwner - Get Process owner of a pid as a string instead of components (#getProcessOwner)


			@return - Returns username if it can be determined, otherwise uid, otherwise "unknown"

		'''


**Commandline**


The following functions get the commandline (executable and arguments) for a running process.


The following function returns a string of the commandline of a running process:

	def getProcessCommandLineStr(pid):

		'''

			getProcessCommandLineStr - Gets a the commandline (program + arguments) of a given pid


			@param pid <int> - Process ID


			@return - None if process not found or can't be determined. Otherwise a string of commandline.


			@note Caution, args may have spaces in them, and you cannot surmise from this method. If you care (like trying to replay a command), use getProcessCommandLineList instead

		'''


The following function returns a list representing the "argv" of a process.

	def getProcessCommandLineList(pid):

		'''

			getProcessCommandLineList - Gets the commandline (program + argumentS) of a given pid as a list.


			@param pid <int> - Process ID


			@return - None if process not found or can't be determined. Otherwise a list representing argv. First argument is process name, remainder are arguments.


			@note - Use this if you care about whether a process had a space in the commands

		'''

**Files**


The following functions deal with open file descriptors (fds) of running processes.


The following function returns information on a process 


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


The following function scans all processes on a system for an open file:

	def scanAllProcessesForOpenFile(searchPortion, isExactMatch=True, ignoreCase=False):

		'''

			scanAllProcessessForOpenFile - Scans all processes on the system for a given filename


				@param searchPortion <str> - Filename to check

				@param isExactMatch <bool> Default True - If match should be exact, otherwise a partial match is performed.

				@param ignoreCase <bool> Default False - If True, search will be performed case-insensitively


			@return - <dict> - A dictionary of pid -> mappingResults for each pid that matched the search pattern. For format of "mappingResults", @see scanProcessForOpenFile

		'''

Current Working Directory
-------------------------

The current working directory (CWD) of a process can be found via:

	def getProcessCwd(pid)

	'''

		getProcessCwd - Gets the cwd (current working directory) of a given pid


		@param pid <int> - Process ID


		@return <str/None> - None if process not found or can't be determined. Otherwise, a string of the CWD

	'''


Also contains scan functions, like those described above, *scanProcessForCwd* and *scanAllProcessessForCwd*.



**General**


The following are general functions

The following function returns a list of all pids running on a system

	def getAllRunningPids()



**Design**


All of the "scan" series of functions return some extra information about the process (owner/cmdline). This is because processes can begin and end quickly, so it's better to get a complete snapshot than to not be able to obtain one later.


Pydoc
=====

Pydoc can be found at: http://pythonhosted.org/ProcessMappingScanner/
