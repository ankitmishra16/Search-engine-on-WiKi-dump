import linecache


#******************************************************************************************************************
# Following function will perform external binary search on the offset file, whose address id passed as 'filename'
# parameter we will open file count lines and then will perform binary search on the file
#******************************************************************************************************************
def binary_search(filename, search_word) :
	
	ret_no = ""

	fp = open(filename, "r")
	no_lines = len(fp.readlines())
	fp.close()

	s = 1
	e = no_lines 

	while s < e :
		mid = ((s + e) // 2)
		line = linecache.getline(filename, mid)
		word = line[:line.index(":")]
		if word == search_word :
			ret_no = line[line.index(":") + 1 : ]
			break
		elif word < search_word :
			s = mid
		elif word > search_word :
			e = mid

	if s == e :
		line = linecache.getline(filename, s)
		word = line[:line.index(":")]
		if word == search_word :
			ret_no = line[line.index(":") + 1 : ]

	return ret_no



