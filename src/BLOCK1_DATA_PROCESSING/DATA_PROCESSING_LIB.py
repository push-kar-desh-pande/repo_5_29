##
# @file   : DATA_PROCESSING_LIB.py 
# @brief  : Library with classes and functions for data cleaning, sentence scoring etc.
# @author : srijeshs
# @date   : 5/23/2020

import sys, os
import logging
import numpy as np

# NLTK includes
from nltk.tokenize import word_tokenize, sent_tokenize, RegexpTokenizer
from nltk.corpus   import stopwords

# ACCESS TO BLOCK0 LIBRARY
sys.path.append( os.path.join( os.path.dirname( __file__ ), 
                               "../BLOCK0_DATA_CURATION" ) )
import DATA_CURATION_LIB as curate
import pdb

# SET OF STOP/FILLER WORDS TO BE FILTERED OUT
STOP_WORDS   = set( stopwords.words( 'english' ) )

class DATA_PROCESSOR:
    '''[BRIEF]: Class for tokenizing and scoring raw string data'''
    
    # Processor parameters 
    SUMMARIZER_TYPE = 'EXTRACTIVE'
    SCORING         = 'TF' 
    WORD_TOKENIZER  = None
    WORD_BLACKLIST  = None

    # Parsed tokens and scores
    WORD_TOKENS     = []
    WORD_SCORES     = {}
    SENTENCE_SCORES = [] 
    REPORTED_SENTECES = []

    def __init__( self,
                  SUMMARIZER_TYPE = 'EXTRACTIVE',  
                  SCORING = 'TF',
                  WORD_TOKENIZER = None,
                  WORD_BLACKLIST = None ):
        '''[BRIEF]: Initialize the DATA_PROCESSOR object specifying a scoring metric
           [NOTE ]: Expand this object to suit algorithm preferences for processing data 
        '''

        self.SCORING         = SCORING
        self.SUMMARIZER_TYPE = SUMMARIZER_TYPE
        
        if not WORD_TOKENIZER:
            self.WORD_TOKENIZER = RegexpTokenizer( r'[a-zA-Z]+' ).tokenize
        else:
            self.WORD_TOKENIZER = WORD_TOKENIZER

        if not WORD_BLACKLIST:
            self.WORD_BLACKLIST = STOP_WORDS
        else:
            self.WORD_BLACKLIST = WORD_BLACKLIST
    
    def WORDS_TOKENIZE( self,
                        RAW_TEXT ):
        '''[BRIEF]: Tokenize raw text into words. 
           [NOTE ]: Further removes non-words, and fillers such as 
                     * Punctuations, 
                     * Conjunctions, 
                     * Prepositions, 
                     * Articles and 
                     * Question words '''
        
        WORD_BLACKLIST  = self.WORD_BLACKLIST
        WORD_TOKENIZER  = self.WORD_TOKENIZER 
        WORDS_FROM_BODY = WORD_TOKENIZER( RAW_TEXT )        
        FILTERED_WORDS  = [ word.lower() for word in WORDS_FROM_BODY 
                            if not word.lower() in WORD_BLACKLIST ]
        
        self.WORD_TOKENS = FILTERED_WORDS

        return

    def SCORE_WORDS( self ):
        '''[BRIEF]: Score each word token according to the registered SCORING metric'''

        WORDSCORE_DICT = { key:0 for key in set( self.WORD_TOKENS ) }

        for word in self.WORD_TOKENS:
            WORDSCORE_DICT[ word ] += 1

        MAX_FREQ = np.max( list( WORDSCORE_DICT.values() ) )

        for key in WORDSCORE_DICT.keys():
            try:
                WORDSCORE_DICT[ key ] = WORDSCORE_DICT[ key ] / MAX_FREQ
            except ZeroDivisionError:
                pass

        self.WORD_SCORES = WORDSCORE_DICT
        return

    def SCORE_SENTENCES( self,
                         HEADERS    = None,
                         PARAGRAPHS = None,
                         WORD_BLACKLIST = None ):
        '''[BRIEF]: Scores each sentence based on the cumulative scores of its words. 
                    The SCORING field is used as the scoring metric '''

        if WORD_BLACKLIST == None:
            WORD_BLACKLIST = self.WORD_BLACKLIST

        # Tokenization of the raw text into words
        for iPara in PARAGRAPHS:
            RAW_SENTENCES  = sent_tokenize( iPara )
            
            idx = 0
            for sentence in RAW_SENTENCES:

                try:
                    SENTENCE_LIST = [ self.WORD_SCORES[ word.lower() ]  
                                      if  word in self.WORD_TOKENS else 0  
                                      for word in self.WORD_TOKENIZER( sentence ) ]
                    
                    if( SENTENCE_LIST ):
                        SENTENCE_SCORE = np.nanmean( SENTENCE_LIST )
                except:
                    pass

                self.SENTENCE_SCORES.append( ( SENTENCE_SCORE, sentence ) )
                idx+=1

        return
       
if ( __name__ == "__main__" ):
    '''[BRIEF]: Sanity for this module by processing a sample article. 
       [NOTE ]: Also low-key tests Block0 here to curate the test data input'''
    
    # BLOCK0: DATA CURATION
    myData   = curate.DATA_CURATER( HEADER_MAXDEPTH = 3 )
    TEST_URL = input( "Enter URL for test ( Uses default URL if blank ): " ) 

    if not TEST_URL:
        TEST_URL = "https://getpocket.com/explore/item/home-sweet-homer-the-strange-saga-of-the-real-life-simpsons-house-in-nevada?utm_source=pocket-newtab"
    
    myData.SCRAPE_URL( SOURCE_URL = TEST_URL )

    # BLOCK1: DATA PROCESSING
    myProcessor = DATA_PROCESSOR( WORD_BLACKLIST = STOP_WORDS )
    myProcessor.WORDS_TOKENIZE( RAW_TEXT = ''.join( myData.PARAGRAPHS ) )
    myProcessor.SCORE_WORDS()
    myProcessor.SCORE_SENTENCES( PARAGRAPHS = myData.PARAGRAPHS )
    
    pdb.set_trace()
