import xml.etree.ElementTree as et
import Stemmer
import contractions
import string
import json
import time
import re
import os

#*********************************************************************************************************************
# Creting a folder 'index' to store all the indicies in it
#*********************************************************************************************************************
root = os.path.dirname(os.path.realpath(__file__))
index_dir = os.path.join(root, "index")

if not os.path.isdir(index_dir) :
    os.mkdir(index_dir)

#*********************************************************************************************************************
# Global variables to store word count in documents, 'count' will store count of documents total processed and 
# 'MAX_ALLOWED' will store number of documents allowed to get written in final index in one go 
#*********************************************************************************************************************
word_count = {}
count = 0
MAX_ALLOWED = 5000

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
        file_path = os.path.join(path, json_file[k])
        js = open(file_path, "w")
        json.dump({}, js)
        js.close()

    special_json = os.path.join(path, 'special_json.json')
    js = open(special_json, "w")
    json.dump({}, js)
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
    try :
        sent = contractions.fix(sent)
    except IndexError :
        sent = sent

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
def write_remaining(include_text) :

    global word_count, count

    if len(word_count) > 0 :
        crr_index = os.path.join(index_dir, str((count//MAX_ALLOWED) + 1))

        if not os.path.isdir(crr_index) :
            os.mkdir(crr_index) 
            create_files(crr_index) 

        for k in word_count.keys() :
            if(not include_text) :
                js = "title_"
            else :
                js = ""
            if k in json_file.keys() :
                js += json_file[k]
            else :
                js += special_json

            js = os.path.join(crr_index, js)
            
            jsf = open(js, 'w')
            json.dump(word_count[k], jsf)
            jsf.close()
            word_count[k].clear()

#*********************************************************************************************************************
# Following is the driver function which will parse the XML file and call tokenize_string(), to get tokenized list of 
# text and then call count_words() to count unique words then update the global dictionary, and if number of documents parsed % MAX_ALLOWED == 0, then 
# dump whole dictionary in respective json file, and clear the dictionary
#*********************************************************************************************************************
def filter_words( filename, include_text ) :

    global word_count, count

    tree = et.parse(filename)
    root = tree.getroot()

    count = 0
    pages = []
    subtags = {}

    for child in root :
        ind = child.tag.find('{http://www.mediawiki.org/xml/export-0.10/}')
        sc = child.tag[ind + len('{http://www.mediawiki.org/xml/export-0.10/}') :]
        if sc == 'page' :
            start = time.time()
            count += 1
            data = {}
            t = ""
            for sch in child :
                ind = sch.tag.find('{http://www.mediawiki.org/xml/export-0.10/}')
                sc = sch.tag[ind + len('{http://www.mediawiki.org/xml/export-0.10/}') :]
                sc.strip()
                if(sc == 'title') :
                    t = str(sch.text)
                    if(len(t) > 0 ) :
                        t = tokenize_string(t)
                    else :
                        t = []

                
                elif(include_text) :
                    if(sc == 'revision' ) :
                        for schh in sch :
                            ind = schh.tag.find('{http://www.mediawiki.org/xml/export-0.10/}')
                            sc = schh.tag[ind + len('{http://www.mediawiki.org/xml/export-0.10/}') :].strip()
                            if sc == 'text' :
                                text = str(schh.text)
                                if(len(text) > 0 ) :
                                    tokenize_s = time.time()
                                    text = tokenize_string(text)
                                    tokenize_e = time.time()
                                else :
                                    text =[]
                        t.extend(text)
            
            count_s = time.time()
            doc_word_count = count_words(t)
            count_e = time.time()
            
            for word in doc_word_count.keys() :
                if word_count.get(word[0]) :
                    if word_count[word[0]].get(word) :
                        word_count[word[0]][word] += (", " + str(count) + ":" + str(doc_word_count[word]) )
                    else :
                        word_count[word[0]][word] = str(str(count) + ":" + str(doc_word_count[word]))
                else :
                    word_count[word[0]] = {}
                    word_count[word[0]][word] = str(str(count) + ":" + str(doc_word_count[word]) )

            if count % MAX_ALLOWED == 0 :
                write_time_s = time.time()
                crr_index = os.path.join(index_dir, str(count//MAX_ALLOWED))

                if not os.path.isdir(crr_index) :
                    os.mkdir(crr_index) 
                    create_files(crr_index) 

                for k in word_count.keys() :
                    if(not include_text) :
                        js = "title_"
                    else :
                        js = ""
                    if k in json_file.keys() :
                        js += json_file[k]
                    else :
                        js += special_json

                    js = os.path.join(crr_index, js)
                    
                    jsf = open(js, 'w')
                    json.dump(word_count[k], jsf)
                    jsf.close()
                    word_count[k].clear()
                write_time_e = time.time()
                print("Time taken to write : ", write_time_e - write_time_s )

    print("Total number of pages are : ", count)

if __name__ == '__main__' :

    include_text = True
    start = time.time()
    filter_words("phase_1.xml", include_text)
    write_remaining(include_text)
    end = time.time()
    print("Time taken : ", end - start)