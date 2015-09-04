# ProcessMappingScanner
Python module for scanning running process mappings (for detecting libraries, executables, etc), and open files.

This module works on UNIX-derived systems only (Linux, BSD, etc)


What is a mapping?
------------------

A mapping can include the running executable (like python), a shared library (like libc) or something else (like a locale-archive file or other mapping).

You can use this module to, for example, scan for running processes to see what is using libpython2.7, or scan a paticular process for a mapping.


Functions
---------

The following function, scanProcessForMapping, scans a single process for mappings. Use an empty string for searchPortion to get all mappings.

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


The following function, scanAllProcessessForMapping, scans all running processes for mappings.

	def scanAllProcessessForMapping(searchPortion):
	'''
	    scanAllProcessessForMapping - Scans all processes on the system for a given search pattern.

	    @return - <dict> - A dictionary of pid -> mappingResults for each pid that matched the search pattern. For format of "mappingResults", @see scanProcessForMapping
	'''
