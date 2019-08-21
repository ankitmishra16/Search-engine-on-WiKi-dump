import xml.etree.ElementTree as et
from nltk.tokenize import word_tokenize, RegexpTokenizer
from nltk.corpus import stopwords
from nltk.stem.wordnet import WordNetLemmatizer
import contractions
import string
import json

def tokenize_string( sent ) :
    #Fixing contractions as don't => do not, etc.
    try :
        sent = contractions.fix(sent)
    except IndexError :
        print("INDEXERROR : ", sent)

    #Tokenization
    sent = word_tokenize(sent)

    #Removing punctuations
    table = str.maketrans('', '', string.punctuation)
    sent = [w.translate(table) for w in sent]

    #Removing special characters
    sent = [ word.lower() for word in sent if word.isalpha()]
    
    #Lemmatization
    lemm = WordNetLemmatizer()
    aa = []
    for word in sent :
        try :
            aa.append(lemm.lemmatize(word))
        except TypeError :
            aa.append(word)
            print(word)
    sent = aa 

    #removing stopwords and case folding to lower case
    sent = [ word.lower() for word in sent if word.lower() not in stopwords.words('english')]

    return sent

def count_words( text ) :
    unique_word_count = {}
    for word in text :
        if word in unique_word_count.keys() :
            unique_word_count[word] += 1
        else :
            unique_word_count[word] = 1

    return unique_word_count

tree = et.parse("phase_1.xml")
root = tree.getroot()

count = 0
pages = []
subtags = {}

for child in root :
    ind = child.tag.find('{http://www.mediawiki.org/xml/export-0.10/}')
    sc = child.tag[ind + len('{http://www.mediawiki.org/xml/export-0.10/}') :]
    if sc == 'page' :
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

            
            elif(sc == 'revision' ) :
                for schh in sch :
                    ind = schh.tag.find('{http://www.mediawiki.org/xml/export-0.10/}')
                    sc = schh.tag[ind + len('{http://www.mediawiki.org/xml/export-0.10/}') :].strip()
                    if sc == 'text' :
                        text = str(schh.text)
                        if(len(text) > 0 ) :
                            text = tokenize_string(text)
                        else :
                            text =[]
        t.extend(text)
        d = count_words(t)
        # d = [text]
        data[count] = d        
        with open('tokens.json', 'a', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

print("Total number of pages are : ", count)

