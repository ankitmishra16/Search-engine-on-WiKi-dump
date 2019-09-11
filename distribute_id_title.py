import os

def distribute(path_to_index, max_file) :
	file = os.path.join(path_to_index, "id_to_title.txt")
	fp = open(file, "r")
	childname = "id_to_title_0.txt"
	child = os.path.join(path_to_index, childname)
	cp = open(child, "w")
	count = 0
	for line in fp :
		count += 1
		cp.write(line)
		if count % max_file == 0 :
			print(count//max_file, " done!!!")
			cp.close()
			cp = childname[:-4]
			child = cp[:cp.index("title_") + 6]
			prev = int(cp[cp.index("title_") + 6 :]) + 1
			childname = child + str(prev) + ".txt"
			child = os.path.join(path_to_index, childname)
			cp = open(child, "w")

if __name__ == "__main__" :
	distribute("./index", 20000)
