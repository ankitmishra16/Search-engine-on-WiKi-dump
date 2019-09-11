import sys, re, os
from tokenization import tokenize_string 
import linecache
import math
import time

path_to_index = ""
field_multiplier = 11
max_file = 20000
#*****************************************************************************************************************
# Following dictionary will store count of lines in offset files, will be used while binary search
#*****************************************************************************************************************
offset_line_count = {}

#*********************************************************************************************************************
# Following dictionary will be used to create index files for words starting from each alphabet, in particular 
# directory, so that it can be easily accessed just by alphabet
#*********************************************************************************************************************
index_file = {'a' : 'a_index.txt', 'b' : 'b_index.txt', 'c' : 'c_index.txt', 'd' : 'd_index.txt', 'e' : 'e_index.txt',
             'f' : 'f_index.txt', 'g' : 'g_index.txt', 'h' : 'h_index.txt', 'i' : 'i_index.txt', 'j' : 'j_index.txt',
             'h' : 'h_index.txt', 'i' : 'i_index.txt', 'j' : 'j_index.txt', 'k' : 'k_index.txt', 'l' : 'l_index.txt',
             'm' : 'm_index.txt', 'n' : 'n_index.txt', 'o' : 'o_index.txt', 'p' : 'p_index.txt', 'q' : 'q_index.txt',
             'r' : 'r_index.txt', 's' : 's_index.txt', 't' : 't_index.txt', 'u' : 'u_index.txt', 'v' : 'v_index.txt',
             'w' : 'w_index.txt', 'x' : 'x_index.txt', 'y' : 'y_index.txt', 'z' : 'z_index.txt' }
special_index = "special_index.txt"

#******************************************************************************************************************
# Following code will initialize offset_line_count dictionary which will be keyed on alphabet of whose offset file
# is being accessed and value will be number of lines that offset file has 
#******************************************************************************************************************
def init_offset_count() :
    global path_to_index, offset_line_count
    offset = os.path.join(path_to_index, "offset_file_length.txt")
    print("File address is : ", offset)
    offset = open(offset, "r")
    for line in offset :
        alpha = line[:line.index(":"):]
        offset_line_count[alpha] = int(line[line.index(":") + 1 :])

    offset.close()


#********************************************************************************************************************
# Following dictionary will store weight for each section indexing on their starting alphabet
#********************************************************************************************************************
section_weight = { "t" : 10, "x" : 5, "C" : 8, "e" : 6, "r" : 7, "i" : 9}

#*******************************************************************************************************************
# Following global variable will store total number of documents in the corpus, will be used to calculate IDF
#*******************************************************************************************************************
total_num_docs = 19567269

def read_file(testfile):
    with open(testfile, 'r') as file:
        queries = file.readlines()
    return queries


def write_file(outputs, path_to_output):
    '''outputs should be a list of lists.
        len(outputs) = number of queries
        Each element in outputs should be a list of titles corresponding to a particular query.'''
    with open(path_to_output, 'w') as file:
        for output in outputs:
            for line in output:
                file.write(line.strip() + '\n')
            file.write('\n')

#*******************************************************************************************************************
# Following function will return TF value from posting list's entery, so that we can use it for calculations
#*******************************************************************************************************************
def get_field_value( value, field ) :
    # print("Value : ", value, ", Field : ", field)
    score = 0
    if "i" in value :
        temp = value.split("i")
        value = temp[0]
        if field == "i" :
            return math.log10(int(temp[1]) * field_multiplier)
        else :
            score += (int(temp[1]) * section_weight["i"])

    if "r" in value :
        temp = value.split("r")
        value = temp[0]
        if field == "r" :
            return math.log10(int(temp[1]) * field_multiplier)
        else :
            score += (int(temp[1]) * section_weight["i"])

    if "e" in value :
        temp = value.split("e")
        value = temp[0]
        if field == "e" :
            return math.log10(int(temp[1]) * field_multiplier)
        else :
            score += (int(temp[1]) * section_weight["i"])

    if "c" in value :
        temp = value.split("c")
        value = temp[0]
        if field == "c" :
            return math.log10(int(temp[1]) * field_multiplier)
        else :
            score += (int(temp[1]) * section_weight["i"])

    if "x" in value :
        temp = value.split("x")
        value = temp[0]
        if field == "x" :
            return math.log10(int(temp[1]) * field_multiplier)
        else :
            score += (int(temp[1]) * section_weight["i"])

    if "t" in value :
        temp = value.split("t")
        value = temp[0]
        if field == "t" :
            return math.log10(int(temp[1]) * field_multiplier)
        else :
            score += (int(temp[1]) * section_weight["i"])
    # print("Score : ", score)
    if field == "a" :
        return math.log10(score)

    return 0

#*******************************************************************************************************************
# Following function will return relevance dictionary for the given field and posting list
#********************************************************************************************************************
def relevance_dictionary( posting, field, word_weight ) :
    
    posting_values = posting.split(",")
    print(len(posting_values))
    ret = {}
    idf = math.log(total_num_docs//len(posting_values))

    for value in posting_values :
        # print("Posting : ", value)
        value = value.strip()
        # print("After strip : ", value,"lll")
        if value == "" :
            continue
        doc = value[:value.index(":")]
        value = value[value.index(":") + 1 :]
        if value == "" :
            continue
        ret[doc] = get_field_value(value, field) * word_weight * idf

    return ret

#********************************************************************************************************************
# Following function will merge two dictionaries, and return resultant dictionary
#******************************************************************************************************************** 
def merge_dicts( org, temp ) :
    for k in temp.keys() :
        if k in org.keys() :
            org[k] += temp[k]
        else :
            org[k] = temp[k]
    return org

#********************************************************************************************************************
# Following function return line on line_number in the filename file
#********************************************************************************************************************
def getline(filename, line_number ) :
    fp = open(filename)
    i = 0
    line = "" 
    while i < line_number :
        line = fp.readline()    
        i += 1
        if line == "" :
            break 
    fp.close()
    return line 

#********************************************************************************************************************
# Following function will be used when multiple lines from same file is required to return in the form of dictionary
# keyed on line number value will be line, and list line_numbers should be sorted, because we search for line, from
# front to rear end sequentially, and we have to featch all the line in on go of file
#********************************************************************************************************************
def get_titles(title_ids) :
    
    global path_to_index
    ret = {}
    id_file = {}

    for ids in title_ids :
        file = ids // max_file
        if file in id_file.keys() :
            id_file[file].append(ids)
        else :
            id_file[file] = [ids]

    for file in id_file.keys() :
        print("id_to_title file number : ", file)
        filename = "id_to_title_" + str(file) + ".txt"
        fp = open(os.path.join(path_to_index, filename), "r")
        for ids in id_file[file] :
            print("Id in search : ", ids)
            # ids = ids.strip()
            run = True
            while run :
                line = fp.readline()
                num = int(line[:line.index(":")])
                if num == ids :
                    run = False
                    ret[num] = line[line.index(":") + 1 :]
        fp.close()
    return ret


#******************************************************************************************************************
# Following function will perform external binary search on the offset file, whose address id passed as 'filename'
# parameter we will open file count lines and then will perform binary search on the file
#******************************************************************************************************************
def binary_search(alphabet, search_words) :
    global path_to_index

    search_words.sort()
    ret = []
    # print("Binary search for : ", search_words)
    no_lines = offset_line_count[alphabet]
    for search_word in search_words :

        file_found = False
        file = ""
        offset_file_1 = alphabet + "_offset_0.txt"
        off1 = open(os.path.join(path_to_index, offset_file_1), "r")

        offset_file_2 = alphabet + "_offset_1.txt"
        if os.path.exists(os.path.join(path_to_index, offset_file_2)) :
            off2 = open(os.path.join(path_to_index, offset_file_2), "r")
        else :
            file_found = True
            file = off1

        # word_1 = off1.readline()
        # word_1 = word_1[word_1.index(":") :]

        while not file_found :
            
            word_2 = off2.readline()
            word_2 = word_2[:word_2.index(":")]

            if search_word < word_2 :
                file_found = True
                file = off1
                filename = offset_file_1
            else :
                # print("Search word : ", search_word, ", word_2 : ", word_2)
                off1.close()
                off1 = off2
                offset_file_1 = offset_file_2
                off2 = offset_file_2[:-4]
                offset_file_2 = off2[:off2.index("offset_") + 7 ]
                prev = int(off2[off2.index("offset_") + 7 :])
                prev += 1
                offset_file_2 = offset_file_2 + str(prev) + ".txt"
                if os.path.exists(os.path.join(path_to_index, offset_file_2)) :
                    off2 = open(os.path.join(path_to_index, offset_file_2), "r")
                else :
                    file_found = True
                    file = off1
                    filename = offset_file_1
        s = 1
        e = max_file - 1
        ret_no = ""
        filename = os.path.join(path_to_index, filename)
        # print("Current word : ", search_word)
        # print("Start : ", s, ", End : ", e)
        while s < e :
            mid = ((s + e) // 2)
            # print(s, " - ", e, "==>", mid)
            # line = linecache.getline(filename, mid)
            line = getline(filename, mid)
            # print("Line : ", line.strip())
            word = line[:line.index(":")].strip()
            if word == search_word :
                # print("Found")
                ret_no = int(line[line.index(":") + 1 : ].strip())
                # print("Line number found : ", ret_no)
                break
            elif word < search_word :
                s = mid + 1
            elif word > search_word :
                e = mid - 1

        if s == e :
            line = getline(filename, s)
            word = line[:line.index(":")]
            if word == search_word :
                # print("Found")
                ret_no = int(line[line.index(":") + 1 : ].strip())
                # print("Line number found : ", ret_no)

        ret.append(ret_no)

    return ret

#********************************************************************************************************************
# Following function will be called for fecthing out posting list, it should return a dictionary indexed on document 
# IDs
#********************************************************************************************************************
def return_postings(query, field) :
    # print("Query words : ", query, ", field : ", field)
    doc_rel_dict = {}
    word_postings = {}
    alpha_words = {}
    titles = []
    query_words = tokenize_string(query) 

    #############################################################################################
    # To segregate words in query in alphabet wise
    #############################################################################################
    query_word_weight = {}
    for word in query_words :
        if word[0] in alpha_words.keys() :
            alpha_words[word[0]].append(word)
        else :
            alpha_words[word[0]] = [word]

        if word in query_word_weight.keys() :
            query_word_weight[word] += 1
        else :
            query_word_weight[word] = 1

    #############################################################################################
    # Following lines will open files using alphabets in query words(first alphabet), and then
    # search for words starting with same alphabet as of file opened respective file, by opening 
    # that file only once
    #############################################################################################
    for alphabet in alpha_words.keys() :
        if alphabet in index_file.keys() :
            filename = index_file[alphabet][:-4]
        else :
            filename = special_index

        alphabetwise_query_words = list(set(alpha_words[alphabet]))
        # offset_file = os.path.join(path_to_index, alphabet + "_offset.txt")
        line_numbers = binary_search( alphabet, alphabetwise_query_words)
        # print("Returned line numbers : ", line_numbers)

        i = 0
        for line_n in line_numbers :
            print("Line number : ", line_n)
            # line = linecache.getline(filename, line_n)
            num = line_n // 20000
            line_n = line_n % 20000
            filename = filename + "_" + str(num) + ".txt"
            filename = os.path.join(path_to_index, filename)
            line = getline(filename, line_n)
            posting = line[line.index(">") + 1 :]
            temp_dict = relevance_dictionary(posting, field, query_word_weight[alphabetwise_query_words[i]])
            doc_rel_dict = merge_dicts(doc_rel_dict, temp_dict)
            i += 1

    return doc_rel_dict

#********************************************************************************************************************
# Following function will be first function to be called for search, it will further check if it is feild query or
# normal query and then accordingly call the appropriate functions 
#********************************************************************************************************************
def search(path_to_index, queries):
    final_output = []
    temp_output = []

    for q in queries :
        title, text, category, references, external, info, all_s = "", "", "", "", "", "", ""
        query_words = re.findall("\d+|[\w|:]+", q)

        for word in query_words :
            # print("\nWord : ", word)
            if "title:" in word :
                # print("word has title : ", word[6:])
                title += (word[6:] + " ") 
            elif "body:" in word :
                # print("Word has body : ", word[5:])
                text += (word[5:] + " ")
            elif "infobox:" in word :
                # print("Word has infobox : ", word[8:])
                info += (word[8:] + " ")
            elif "category:" in word :
                # print("Word has category : ", word[9:])
                category += (word[9:] + " ")
            elif "ref:" in word :
                # print("Word has ref : ", word[4:])
                references += (word[4:] + " ")
            elif "ext:" in word :
                # print("Word has ext : ", word[4:])
                external += (word[4:] + " ")
            else :
                # print("Word has no field query")
                all_s += (word + " ")

        if len(title) > 0 :
            title = return_postings(title, "t")
        else :
            title = {}
        if len(text) > 0 :
            text = return_postings(text, "x")
        else :
            text = {}
        if len(category) > 0 :
            category = return_postings(category, "c")
        else :
            category = {}
        if len(references) > 0 :
            references = return_postings(references, "r")
        else :
            references = {}
        if len(external) > 0 :
            external = return_postings(external, "e")
        else :
            external = {}
        if len(info) > 0 :
            info = return_postings(info, "i")
        else :
            info = {}
        if len(all_s) > 0 :
            all_s = return_postings(all_s, "a")
        else :
            all_s = {}

        total_docs = set(list(title.keys()) + list(text.keys()) + list(category.keys()) + list(references.keys()) +
                         list(external.keys()) + list(info.keys()) + list(all_s.keys()) )

        final_rel_doc = {}
        final_rel_l = []
        for doc in total_docs :
            score = 0
            if doc in title.keys() :
                score += title[doc]

            if doc in text.keys() :
                score += text[doc]

            if doc in category.keys() :
                score += category[doc]

            if doc in references.keys() :
                score += references[doc]

            if doc in external.keys() :
                score += external[doc]

            if doc in info.keys() :
                score += info[doc]

            if doc in all_s.keys() :
                score += all_s[doc]

            if score not in final_rel_l :
                final_rel_l.append(score)
                final_rel_doc[score] = [doc]
            else :
                final_rel_doc[score].append(doc)

        final_rel_l.sort()
        final_rel_l.reverse()
        count = min(10, len(final_rel_l))
        doc_IDs = []
        i = 0
        while len(doc_IDs) < 10 : 
            for d_id in final_rel_doc[final_rel_l[i]] :
                doc_IDs.append(int(d_id))
            i += 1

        # id_to_title = os.path.join(path_to_index, "id_to_title.txt")
        print("Doc IDs to return : ", doc_IDs)
        sorted_docIDs = doc_IDs
        sorted_docIDs.sort()
        lines = get_titles(sorted_docIDs)
        for ids in doc_IDs :
            line = lines[ids]
            # line = getline(id_to_title, int(ids)).strip()
            temp_output.append(line)
            print("Appended doc : ", line)

        final_output.append(temp_output)
        temp_output = []

    return final_output


def main():
    global path_to_index, total_num_docs
    path_to_index = sys.argv[1]
    testfile = sys.argv[2]
    path_to_output = sys.argv[3]

    s = time.time()
    init_offset_count()
    queries = read_file(testfile)
    fp = open(os.path.join(path_to_index, "total_docs.txt"), "r")
    total_num_docs = int(fp.readline().strip())
    fp.close()
    outputs = search(path_to_index, queries)
    write_file(outputs, path_to_output)
    e = time.time()
    print("TIme taken : ", e - s)

if __name__ == '__main__':
    main()
