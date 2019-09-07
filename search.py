import sys, re, os
from tokenization import tokenize_string 
import linecache
import math

path_to_index = ""
field_multiplier = 11

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

#********************************************************************************************************************
# Following dictionary will store weight for each section indexing on their starting alphabet
#********************************************************************************************************************
section_weight = { "t" : 10, "x" : 5, "C" : 8, "e" : 6, "r" : 7, "i" : 9}

#*******************************************************************************************************************
# Following global variable will store total number of documents in the corpus, will be used to calculate IDF
#*******************************************************************************************************************
total_num_docs = ""

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

    score = 0
    if "i" in value :
        temp = value.split("i")
        value = temp[0]
        if field == "i" :
            return math.log10(temp[1] * field_multiplier)
        else :
            score += (int(temp[1]) * section_weight["i"])

    if "r" in value :
        temp = value.split("r")
        value = temp[0]
        if field == "r" :
            return math.log10(temp[1] * field_multiplier)
        else :
            score += (int(temp[1]) * section_weight["i"])

    if "e" in value :
        temp = value.split("e")
        value = temp[0]
        if field == "e" :
            return math.log10(temp[1] * field_multiplier)
        else :
            score += (int(temp[1]) * section_weight["i"])

    if "c" in value :
        temp = value.split("c")
        value = temp[0]
        if field == "c" :
            return math.log10(temp[1] * field_multiplier)
        else :
            score += (int(temp[1]) * section_weight["i"])

    if "x" in value :
        temp = value.split("x")
        value = temp[0]
        if field == "x" :
            return math.log10(temp[1] * field_multiplier)
        else :
            score += (int(temp[1]) * section_weight["i"])

    if "t" in value :
        temp = value.split("t")
        value = temp[0]
        if field == "t" :
            return math.log10(temp[1] * field_multiplier)
        else :
            score += (int(temp[1]) * section_weight["i"])

    if field == "a" :
        return math.log10(score)

#*******************************************************************************************************************
# Following function will return relevance dictionary for the given field and posting list
#********************************************************************************************************************
def relevance_dictionary( posting, field, word_weight ) :
    posting_values = posting.split(", ")
    ret = {}
    idf = math.log(total_num_docs//len(posting_values))

    for value in posting_values :
        doc = value[:value.index(":")]
        value = value[value.index(":") + 1 :]
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

#******************************************************************************************************************
# Following function will perform external binary search on the offset file, whose address id passed as 'filename'
# parameter we will open file count lines and then will perform binary search on the file
#******************************************************************************************************************
def binary_search(filename, search_words) :
    
    ret = []

    fp = open(filename, "r")
    no_lines = len(fp.readlines())
    fp.close()
    for search_word in search_words :
        s = 1
        e = no_lines 
        ret_no = ""

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

        ret.append(ret_no)

    return ret

#********************************************************************************************************************
# Following function will be called for fecthing out posting list, it should return a dictionary indexed on document 
# IDs
#********************************************************************************************************************
def return_postings(query, field) :
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
            filename = index_file[alphabet]
        else :
            filename = special_index

        filename = os.path.join(path_to_index, filename)
        alphabetwise_query_words = set(alpha_words[alphabet])
        line_numbers = binary_search(filename, alphabetwise_query_words)

        i = 0
        for line_n in line_numbers :
            if line_n == "" :
                continue
            line_n = int(line_n)
            line = linecache.getline(filename, line_n)
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
        query_words = re.findall("\d+|[\w]+", q)

        for word in query_words :
            if "title:" in word :
                title += (word[6:] + " ") 
            elif "body:" in word :
                text += (word[5:] + " ")
            elif "infobox:" in word :
                info += (word[8:] + " ")
            elif "category:" in word :
                category += (word[9:] + " ")
            elif "ref:" in word :
                references += (word[4:] + " ")
            elif "ext:" in word :
                external += (word[4:] + " ")
            else :
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

            final_rel_l.append(score)
            final_rel_doc[score] = doc

        final_rel_l.sort()
        final_rel_l.reverse()
        count = min(10, len(final_rel_l))
        doc_IDs = []
        for i in range(count) : 
            doc_IDs.append(final_rel_doc[final_rel_l[i]])

        id_to_title = os.path.join(path_to_index, "id_to_title.txt")
        for ids in doc_IDs :
            line = linecache.getline(id_to_title, int(ids)).strip()
            temp_output.append(line[line.index(":") + 1 :])

        final_output.append(temp_output)
        temp_output = []

    return final_output


def main():
    global path_to_index, total_num_docs
    path_to_index = sys.argv[1]
    testfile = sys.argv[2]
    path_to_output = sys.argv[3]

    queries = read_file(testfile)
    fp = open("total_docs.txt", "r")
    total_num_docs = int(fp.readline().strip())
    fp.close()
    outputs = search(path_to_index, queries)
    write_file(outputs, path_to_output)


if __name__ == '__main__':
    main()
