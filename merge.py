import string
import os
import heapq
import time

index_file = {'a' : 'a_index.txt', 'b' : 'b_index.txt', 'c' : 'c_index.txt', 'd' : 'd_index.txt', 'e' : 'e_index.txt',
             'f' : 'f_index.txt', 'g' : 'g_index.txt', 'h' : 'h_index.txt', 'i' : 'i_index.txt', 'j' : 'j_index.txt',
             'h' : 'h_index.txt', 'i' : 'i_index.txt', 'j' : 'j_index.txt', 'k' : 'k_index.txt', 'l' : 'l_index.txt',
             'm' : 'm_index.txt', 'n' : 'n_index.txt', 'o' : 'o_index.txt', 'p' : 'p_index.txt', 'q' : 'q_index.txt',
             'r' : 'r_index.txt', 's' : 's_index.txt', 't' : 't_index.txt', 'u' : 'u_index.txt', 'v' : 'v_index.txt',
             'w' : 'w_index.txt', 'x' : 'x_index.txt', 'y' : 'y_index.txt', 'z' : 'z_index.txt', 
             "special" : "special_index.txt"}
# special_file = 'special_index.txt'

def next_line(fpt) :
	try :
		temp = fpt.readline()
	except ValueError :
		print("---------------------------------------------------------------------------------------------------")
		print("Passed file pointer is : ", fp)
		print("---------------------------------------------------------------------------------------------------")
		raise(ValueError)
	temp = temp.strip()
	if len(temp) > 0 :
		word = temp[:temp.index("--->")]
		posting = temp[len(word) + 4 : ]
	else :
		word, posting = "", ""
	return word, posting

def merge_files( iter_count, index_dir ) :
	alphabets = list(index_file.keys())

	for a in alphabets :
		line_count = 0
		# Creating final index files 
		file = os.path.join(index_dir, index_file[a])
		fp = open(file, "w")

		#Creating an offset file to store word with line number on which this word is stored in its first alphabet's
		# index file
		offset = a + "_offset.txt"
		offset = os.path.join(index_dir, offset)
		offset = open(offset, "w")

		# Storing all the file pointers in file_pointers list to access those files
		file_pointers = []
		for i in range(iter_count) :
			temp = os.path.join(index_dir, str(i + 1))
			if os.path.exists(temp) :
				temp = os.path.join(temp, index_file[a])
				if os.path.exists(temp) :
					temp = open(temp, "r")
					file_pointers.append(temp)
				else :
					print("File : ", temp, " does not exist!!!!!!!!!")
			else :
				print("Directory : ", temp, " does not exist!!!!!!!!!")

		postings = {}
		from_file = {}
		heap = []
		i = 0
		for fpt in file_pointers :
			word, posting = next_line(fpt)
			
			while word in postings.keys() :
				temp = ", "
				temp += posting
				postings[word] += temp
				word, posting = next_line(fpt)

			from_file[word] = file_pointers.index(fpt)
			postings[word] = posting
			heap.append(word)
			i += 1

		heapq.heapify(heap)

		while len(heap) > 0 :
			word = heapq.heappop(heap)
			posting = postings[word]
			pos_list = word + "--->" + posting + "\n"
			fp.write(pos_list)

			line_count += 1
			off = word + ":" + str(line_count) + "\n"
			offset.write(off)

			ind = from_file[word]
			del from_file[word]
			del postings[word]
			fpt = file_pointers[ind]
			word, posting = next_line(fpt)

			if len(word) > 0 :
				while word in postings.keys() :
					temp = ", "
					temp += posting
					postings[word] += temp
					word, posting = next_line(fpt)
					if len(word) == 0 :
						break

			if len(word) > 0 :
				from_file[word] = ind
				postings[word] = posting
				heapq.heappush(heap, word)
			else :
				fpt.close()
				# print("Closing : ", ind)
				# print(list(from_file.values()))
				# print(file_pointers)


		offset.close()
		fp.close()
		# print("For alphabet '", a, "' merging is done!!!!" )

if __name__ == "__main__" :
	s = time.time()
	merge_files(3, "./index_latest" )
	e = time.time()
	print("Time taken : ", e - s)