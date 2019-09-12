# Search-engine-on-WiKi-dump
This respository contains code of making an efficient search engine on WIki dump

## Creating index
 tokenization.py is a file responsible for creating index, it has different modules for different purposes, like preprocessing text, making index, merging all intermediate files to create final index, etc.
 
 To run tokenization.py we have to run following command :
 
 "python3 tokenization.py wiki_dump_address index_dir_address"
 
 Where,
 
      wiki_dum_address : It will be address where wiki dump is store, it cab be relavtive or absolute
      
      inde_dir_address : It will be address where user wants to store his/her indexes, if the final folder does not exist it will automatically get created, but only the final folder not the heiriearchy

Stemmer.py is a file which have code of Porter stemmer, we had used this way of using it instead of nltk library in interest of time efficiency

merge.py is a file which have all the code for meging all the intermediate file, to produce final indexes

## Searching
  search.py is a file which have all the code for searching, it imports a function from tokenization.py to pre-process query strings
  
  To run search.py we have to run following command :
  
  "python3 search.py index_dir_address"
  
  Where,
  
        index_dir_address : Address where all the final indexes were stored
        
  while running, program will take input(query) from terminal, and it will return titles of relevant documents in decreasing order from top-to-down,and it will be in loop until user opt to go out of it.
