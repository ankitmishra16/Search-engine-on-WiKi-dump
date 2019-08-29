import xml.etree.ElementTree as et
import Stemmer
import string
import time
import re
import os, sys

#*********************************************************************************************************************
# Format of index is doc_id:title count, text count, category count, external links count, references count, infobox count
# Example : 34:t23x42c10e7r3i15, it means document with id 34 has this word 23 times in title, 42 times in text, 
# 10 times in category, 7 times in external links, 3 times in references and 15 times in infobox
# -->If word is not present in any section that section is not illustrated with 0 in index rather it was eliminated from index
# to reduce size of index
#   ---> We will change the value to 'term frequncy', which will be obtained by dividing number of occurences by total number
# of terms in that section
#*********************************************************************************************************************

#*********************************************************************************************************************
# Creting a folder 'index' to store all the indicies in it
#*********************************************************************************************************************
# root_dir = os.path.dirname(os.path.realpath(__file__))
index_dir = ""

#*********************************************************************************************************************
# Global variables to store word count in documents, 'count' will store count of documents total processed and 
# 'MAX_ALLOWED' will store number of documents allowed to get written in final index in one go 
#*********************************************************************************************************************
total_word_count = {}
count = 0
MAX_ALLOWED = 28700

#*********************************************************************************************************************
# Following dictionary will be used to create index files for words starting from each alphabet, in particular 
# directory, so that it can be easily accessed just by alphabet
#*********************************************************************************************************************
json_file = {'a' : 'a_index.json', 'b' : 'b_index.json', 'c' : 'c_index.json', 'd' : 'd_index.json', 'e' : 'e_index.json',
             'f' : 'f_index.json', 'g' : 'g_index.json', 'h' : 'h_index.json', 'i' : 'i_index.json', 'j' : 'j_index.json',
             'h' : 'h_index.json', 'i' : 'i_index.json', 'j' : 'j_index.json', 'k' : 'k_index.json', 'l' : 'l_index.json',
             'm' : 'm_index.json', 'n' : 'n_index.json', 'o' : 'o_index.json', 'p' : 'p_index.json', 'q' : 'q_index.json',
             'r' : 'r_index.json', 's' : 's_index.json', 't' : 't_index.json', 'u' : 'u_index.json', 'v' : 'v_index.json',
             'w' : 'w_index.json', 'x' : 'x_index.json', 'y' : 'y_index.json', 'z' : 'z_index.json' }
special_json = 'special_json.json'

#************************************************************************************************************************
#initialising stopword's dictionary using stopwords.txt file
#************************************************************************************************************************
sp = open('stopwords.txt', 'r')
stp = {}
for word in sp :
    stp[word.strip()] = 1
sp.close()  

#*********************************************************************************************************************
# Following function will be used to create files for each alphabet and special characters, this function will be 
# called only once, whenever any directory is created
#*********************************************************************************************************************

def create_files( path ) :
    for k in json_file.keys() :
        file_path = os.path.join(path, json_file[k][:-4] + "txt")
        js = open(file_path, "w")
        json.dump({}, js)
        js.close()

    special_json = os.path.join(path, 'special_json.txt')
    js = open(special_json, "w")
    # json.dump({}, js)
    js.close() 

#************************************************************************************************************************
# Function to tokenize string using regular expression library
#************************************************************************************************************************
def tokenize(data):                                                 
    tokenisedWords=re.findall("\d+|[\w]+",data)
    return tokenisedWords

#************************************************************************************************************************
# Function to remove stopwords and puctuations from list(passed as parameter) of tokens, and after that stemming is 
# also done
#************************************************************************************************************************
def remove_stopwords(data) :
    table = str.maketrans('', '', string.punctuation)
    result = []
    for word in data :
        if( word.isalpha() ) :
            word = word.strip()
            word = word.translate(table)
            word = word.strip()
            if len(word) > 2 :
                try :
                    if stp[word.strip()] != 1 :
                        result.append(str(Stemmer.stem(word)).lower())
                except KeyError :
                    result.append(str(Stemmer.stem(word)).lower())

    return result

#*********************************************************************************************************************
# --> Following function will be called first to tokenize string, after that, this function will use helper function to 
# tokenize(tokenize()) and remove stopwords, punctuations and stemming(remove_stopwords())
# --> Contractions are also perfomed on string passed as 'sent'(parameter), i.e., your=>you are, don't=>do not, etc.
#*********************************************************************************************************************
def tokenize_string( sent ) :

    if len(sent) == 0 :
        return []

    sent = tokenize(sent)
    result = remove_stopwords(sent)

    return result 
#*********************************************************************************************************************
# Following function counts number of unique words in given list(parameter) 'text', and returns a dictionary having 
# keyed on unique word and value as count of their occurences in passed list
#*********************************************************************************************************************
def count_words( text ) :
    unique_word_count = {}
    for word in text :
        if word in unique_word_count.keys() :
            unique_word_count[word] += 1
        else :
            unique_word_count[word] = 1

    return unique_word_count

#*********************************************************************************************************************
# Following function will be called after all the processing is done, to write down last fraction of index in a 
# json file, as we are writing in json only after count % MAX_ALLOWED == 0, so it is possible that last fragment may 
# be less than MAX_ALLOWED so it won't get written in that way, hence we have to write an auxillary function for it
#*********************************************************************************************************************
def write_remaining( ) :

    global total_word_count, count

    if len(total_word_count) > 0 :
        # crr_index = os.path.join(index_dir, str((count//MAX_ALLOWED) + 1))
        crr_index = index_dir

        if not os.path.isdir(crr_index) :
            os.mkdir(crr_index) 
            create_files(crr_index) 

        for k in total_word_count.keys() :
            js = ""
            if k in json_file.keys() :
                js += json_file[k]
            else :
                js += special_json

            js = js[:-4] + "txt"
            js = os.path.join(crr_index, js)
            
            jsf = open(js, 'w')
            # json.dump(total_word_count[k], jsf)
            for word in total_word_count[k].keys() :
                jsf.write(total_word_count[k][word] + "\n")
            jsf.close()
            total_word_count[k].clear()

#*********************************************************************************************************************
# Following function will filter out and do all the preprocessing(tokenization, stemming, case folding and removal of 
# stopwords) on the words in categories
#*********************************************************************************************************************
def filter_categories( data ) :
    
    d_list = data.split("\n")
    
    if len(d_list) == 0 :
        return []

    cat_string = ( d_list[0].split("]]")[0] + " " )
    i = 1
    while i < len(d_list) :
        if "[[Category:" in d_list[i] :
            cat_string += (d_list[i].split("[[Category:")[1].split("]]")[0].strip() + " ")
        i += 1

    categories = tokenize_string(cat_string)
    return categories

#*********************************************************************************************************************
# Following function will filter out and do all the preprocessing(tokenization, stemming, case folding and removal of 
# stopwords) on the words in External links
#*********************************************************************************************************************
def filter_external_links( data ) :
    if len(data) == 0 :
        return []

    link_string = ""
    d_list = data.split("\n")
    for i in range(len(d_list)) :
        line = d_list[i].strip()
        if len(line) == 0 :
            continue
        if "* [" in line or "*[" in line :
            try :
                temp = line.split("[")[1][:-1]
            except IndexError :
                print(line)
                sys.exit()
            # temp = d_list[i].split("[")[1][:-1]
            temp = temp.split(" ")
            for word in temp :
                if "http" not in word :
                    link_string += (word.strip() + " ")

    link_tokens = tokenize_string(link_string)
    return link_tokens

#*********************************************************************************************************************
# Following function will filter out and do all the preprocessing(tokenization, stemming, case folding and removal of 
# stopwords) on the words in References
#*********************************************************************************************************************
def filter_references( data ) :
    if len(data) == 0 :
        return []

    d_list = data.split("\n")
    references_string = ""
    references = []
    for i in range(len(d_list)) :
        temp = d_list[i].strip().lower()
        if "{{DEFAULTSORT:" in temp or temp[0:2] == "==" and temp[-2:] == "==" :
            break 
        else :
            if "reflist" not in temp :
                references_string += temp 

    references = tokenize_string(references_string)
    return references

#*********************************************************************************************************************
# Following function will filter out and do all the preprocessing(tokenization, stemming, case folding and removal of 
# stopwords) on the words in Infobox
#*********************************************************************************************************************
def filter_infobox_text( data ) :
    if len(data) == 0 :
        return [], []

    d_list = data.split("\n")
    info_string, text_string = "", ""
    i = 0
    while i < len(d_list) :
        temp = d_list[i].strip()
        if "{{Infobox" in temp :
            # info_string += temp.split("{{Infobox")[1]
            brace_open = 0
            while True :
                if "{{" in temp :
                    brace_open += temp.count("{{")
                if "}}" in temp :
                    brace_open -= temp.count("}}")

                if "=" in temp :
                    info_string += temp.split("=")[1]
                elif "{{Infobox" in temp :
                    info_string += temp.split("{{Infobox")[1]
                else :
                    info_string += temp

                if brace_open <= 0 :
                    break ;

                i += 1
                if i < len(d_list) :
                    temp = d_list[i]
                else :
                    break 
        else :
            text_string += temp 

        i += 1

    text = tokenize_string( text_string )
    info = tokenize_string( info_string )
    return info, text

#*********************************************************************************************************************
# Following function will calculate term frequency for passed term's data i.e.,  number of ocuucrence of that term in
# document/section of document, and total number of terms in that 
#*********************************************************************************************************************
def term_frequency( occurence_count, total_terms ) :
    ret = ""
    try :
        ret = str(round((occurence_count/total_terms), 4 ) )
    except ZeroDivisionError : 
        ret = "0.0"

    ret = ret[ret.index(".") + 1 :]
    return ret

#*********************************************************************************************************************
# Following is the driver function which will parse the XML file and call tokenize_string(), to get tokenized list of 
# text and then call count_words() to count unique words then update the global dictionary, and if number of documents parsed % MAX_ALLOWED == 0, then 
# dump whole dictionary in respective json file, and clear the dictionary
#*********************************************************************************************************************
def filter_words( filename ) :

    global total_word_count, count

    tree = et.parse(filename)
    root = tree.getroot()

    count = 0
    docID_title = ""

    for child in root :
        ind = child.tag.find('{http://www.mediawiki.org/xml/export-0.10/}')
        sc = child.tag[ind + len('{http://www.mediawiki.org/xml/export-0.10/}') :]
        if sc == 'page' :
            start = time.time()
            count += 1
            data = {}
            title = ""
            for sch in child :
                ind = sch.tag.find('{http://www.mediawiki.org/xml/export-0.10/}')
                sc = sch.tag[ind + len('{http://www.mediawiki.org/xml/export-0.10/}') :]
                sc.strip()
                if(sc == 'title') :
                    title = str(sch.text)
                    docID_title += ( str(count) + ":" + title + "\n")
                    if(len(title) > 0 ) :
                        title = tokenize_string(title)
                    else :
                        title = []

                
                elif(sc == 'revision' ) :
                    for schh in sch :
                        ind = schh.tag.find('{http://www.mediawiki.org/xml/export-0.10/}')
                        sc = schh.tag[ind + len('{http://www.mediawiki.org/xml/export-0.10/}') :].strip()
                        if sc == 'text' :
                            text = str(schh.text)
                            
                            #Fetching out category from text corpus
                            text = text.split("[[Category:")
                            if len(text) > 1 and len(text[1]) > 0 :
                                category = text[1]
                            else :
                                category = ""
                            text = text[0]
                            category = filter_categories(category)

                            #Fetching out reference from text corpus
                            text = text.split("==External links==")
                            if len(text) > 1 and len(text[1]) > 0 :
                                e_links = text[1]
                            else :
                                e_links = ""
                            text = text[0]
                            e_links = filter_external_links(e_links)

                            #Fetching out reference from text corpus
                            text = text.split("==References==")
                            if len(text) > 1 and len(text[1]) > 0 :
                                references = text[1]
                            else :
                                references = ""
                            text = text[0]
                            references = filter_references(references)

                            #Filtering and tokenizing infobox and text part
                            infobox, text = filter_infobox_text(text)

            title_count = count_words(title)
            text_count = count_words(text)
            infobox_count = count_words(infobox)
            references_count = count_words(references)
            e_links_count = count_words(e_links)
            category_count = count_words(category)

            title_total = len(title_count)
            text_total = len(text_count)
            infobox_total = len(infobox_count)
            references_total = len(references_count)
            e_links_total = len(e_links_count)
            category_total = len(category_count)
            
            vocabulary = set( list(title_count.keys()) + list(text_count.keys()) + list(infobox_count.keys())
                              + list(references_count.keys()) + list(e_links_count.keys()) + list(category_count.keys()) )

            for word in vocabulary :
                string = ""
                
                #For title part
                string += "t"
                try :
                    temp = title_count[word] 
                except KeyError :
                    temp = 0
                temp = term_frequency(temp, title_total)
                if temp != "0" :
                    string += temp
                else :
                    string = string[:-1]

                #For text part
                string += "x"
                try :
                    temp = text_count[word] 
                except KeyError :
                    temp = 0
                temp = term_frequency(temp, text_total)
                if temp != "0" :
                    string += temp
                else :
                    string = string[:-1]

                #For category part
                string += "c"
                try :
                    temp = category_count[word] 
                except KeyError :
                    temp = 0
                temp = term_frequency(temp, category_total)
                if temp != "0" :
                    string += temp
                else :
                    string = string[:-1]

                #For external links part
                string += "e"
                try :
                    temp = e_links_count[word] 
                except KeyError :
                    temp = 0
                temp = term_frequency(temp, e_links_total)
                if temp != "0" :
                    string += temp
                else :
                    string = string[:-1]

                #For references part
                string += "r"
                try :
                    temp = references_count[word] 
                except KeyError :
                    temp = 0
                temp = term_frequency(temp, references_total)
                if temp != "0" :
                    string += temp
                else :
                    string = string[:-1]

                #For infobox part
                string += "i"
                try :
                    temp = infobox_count[word] 
                except KeyError :
                    temp = 0
                temp = term_frequency(temp, infobox_total)
                if temp != "0" :
                    string += temp
                else :
                    string = string[:-1]

                if total_word_count.get(word[0]) :
                    if total_word_count[word[0]].get(word) :
                        total_word_count[word[0]][word] += (", " + str(count) + ":" + string )
                    else :
                        total_word_count[word[0]][word] = word + "--->" + str(str(count) + ":" + string)
                else :
                    total_word_count[word[0]] = {}
                    total_word_count[word[0]][word] = word + "--->" + str(str(count) + ":" + string )

            if count % MAX_ALLOWED == 0 :
                write_time_s = time.time()
                # crr_index = os.path.join(index_dir, str(count//MAX_ALLOWED))
                crr_index = index_dir

                if not os.path.isdir(crr_index) :
                    os.mkdir(crr_index) 
                    create_files(crr_index) 

                for k in total_word_count.keys() :
                    js = ""
                    if k in json_file.keys() :
                        js += json_file[k]
                    else :
                        js += special_json
                    js = js[:-4] + "txt"
                    js = os.path.join(crr_index, js)
                    
                    jsf = open(js, 'w')
                    # json.dump(total_word_count[k], jsf)
                    for word in total_word_count[k].keys() :
                        jsf.write(total_word_count[k][word] + "\n")
                    jsf.close()
                    total_word_count[k].clear()
                write_time_e = time.time()
                # print("Time taken to write : ", write_time_e - write_time_s )
    ID_title_map = os.path.join(index_dir, "id_to_title.txt")
    idt = open(ID_title_map, "w")
    idt.write(docID_title)
    idt.close()

    # print("Total number of pages are : ", count)

def main() :
    global index_dir
    wiki_dump = sys.argv[1]
    index_dir = sys.argv[2]
    
    if not os.path.isdir(index_dir) :
        os.mkdir(index_dir)

    include_text = True
    start = time.time()
    filter_words(wiki_dump)
    write_remaining()
    end = time.time()
    print("Time taken : ", end - start)

if __name__ == '__main__' :
    main()
