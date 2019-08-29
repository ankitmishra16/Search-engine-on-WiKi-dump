import sys, re, os
from tokenization import tokenize_string 
import linecache

path_to_index = ""
field_multiplier = 11

#*********************************************************************************************************************
# Following dictionary will be used to create index files for words starting from each alphabet, in particular 
# directory, so that it can be easily accessed just by alphabet
#*********************************************************************************************************************
index_file = {'a' : 'a_index.json', 'b' : 'b_index.json', 'c' : 'c_index.json', 'd' : 'd_index.json', 'e' : 'e_index.json',
             'f' : 'f_index.json', 'g' : 'g_index.json', 'h' : 'h_index.json', 'i' : 'i_index.json', 'j' : 'j_index.json',
             'h' : 'h_index.json', 'i' : 'i_index.json', 'j' : 'j_index.json', 'k' : 'k_index.json', 'l' : 'l_index.json',
             'm' : 'm_index.json', 'n' : 'n_index.json', 'o' : 'o_index.json', 'p' : 'p_index.json', 'q' : 'q_index.json',
             'r' : 'r_index.json', 's' : 's_index.json', 't' : 't_index.json', 'u' : 'u_index.json', 'v' : 'v_index.json',
             'w' : 'w_index.json', 'x' : 'x_index.json', 'y' : 'y_index.json', 'z' : 'z_index.json' }
special_index = 'special_json.json'

#********************************************************************************************************************
# Following dictionary will store weight for each section indexing on their starting alphabet
#********************************************************************************************************************
section_weight = { "t" : 10, "x" : 5, "C" : 8, "e" : 6, "r" : 7, "i" : 9}

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
            return temp[1] * field_multiplier
        else :
            score += (int(temp[1]) * section_weight["i"])

    if "r" in value :
        temp = value.split("r")
        value = temp[0]
        if field == "r" :
            return temp[1] * field_multiplier
        else :
            score += (int(temp[1]) * section_weight["i"])

    if "e" in value :
        temp = value.split("e")
        value = temp[0]
        if field == "e" :
            return temp[1] * field_multiplier
        else :
            score += (int(temp[1]) * section_weight["i"])

    if "c" in value :
        temp = value.split("c")
        value = temp[0]
        if field == "c" :
            return temp[1] * field_multiplier
        else :
            score += (int(temp[1]) * section_weight["i"])

    if "x" in value :
        temp = value.split("x")
        value = temp[0]
        if field == "x" :
            return temp[1] * field_multiplier
        else :
            score += (int(temp[1]) * section_weight["i"])

    if "t" in value :
        temp = value.split("t")
        value = temp[0]
        if field == "t" :
            return temp[1] * field_multiplier
        else :
            score += (int(temp[1]) * section_weight["i"])

    if field == "a" :
        return score

#*******************************************************************************************************************
# Following function will return relevance dictionary for the given field and posting list
#********************************************************************************************************************
def relevance_dictionary( posting, field ) :
    posting_values = posting.split(", ")
    ret = {}

    for value in posting_values :
        doc = value[:value.index(":")]
        value = value[value.index(":") + 1 :]
        ret[doc] = get_field_value(value, field)

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
    for word in query_words :
        if word[0] in alpha_words.keys() :
            alpha_words[word[0]].append(word)
        else :
            alpha_words[word[0]] = [word]

    #############################################################################################
    # Following lines will open files using alphabets in query words(first alphabet), and then
    # search for wards starting with same alphabet in respective file, by opening that file only
    # once
    #############################################################################################
    for alphabet in alpha_words.keys() :
        if alphabet in index_file.keys() :
            filename = index_file[alphabet]
        else :
            filename = special_index

        filename = filename[:-4] + "txt"
        filename = os.path.join(path_to_index, filename)
        file = open(filename, "r")
        alphabetwise_query_word = set(alpha_words[alphabet])
        for line in file :
            if len(alphabetwise_query_word) == 0 :
                break ;
            word = line[:line.index("--->")]
            posting = line[line.index(">") + 1 :]
            if word in alphabetwise_query_word :
                temp_dict = relevance_dictionary(posting, field)
                doc_rel_dict = merge_dicts(doc_rel_dict, temp_dict)
                alphabetwise_query_word.remove(word)
        file.close()

    return doc_rel_dict
    # rel_doc = {}
    # rel_doc_l = []
    # for k in doc_rel_dict.keys() :
    #     rel_doc[doc_rel_dict[k]] = k
    #     rel_doc_l.append(doc_rel_dict[k])

    # doc_rel_l.sort()
    # count = min(15, len(doc_rel_dict))
    # for i in range(count) :
    #     doc_IDs.append(rel_doc[rel_doc_l[i]])

    # for ids in doc_IDs :
    #     line = linecache.getline("id_to_title.txt", ids).strip()
    #     titles.append(line[line.index(":") + 1 :])

    # return titles

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
        count = min(15, len(final_rel_l))
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
    global path_to_index
    path_to_index = sys.argv[1]
    testfile = sys.argv[2]
    path_to_output = sys.argv[3]

    queries = read_file(testfile)
    outputs = search(path_to_index, queries)
    write_file(outputs, path_to_output)


if __name__ == '__main__':
    main()
