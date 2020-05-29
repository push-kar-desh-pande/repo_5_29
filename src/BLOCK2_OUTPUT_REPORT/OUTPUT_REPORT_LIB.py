##
# @file   : OUTPUT_REPORT_LIB.py 
# @brief  : Library with classes and functions for reporting outputs and GUI interactions
# @author : srijeshs
# @date   : 5/24/2020

# TODO: Add logging wherever appropriate
import sys, os
import numpy as np
import logging
import datetime
import requests, urllib
from io  import BytesIO
from PIL import Image
import pdb


# ACCESS TO BLOCK0 ANF BLOCK1 LIBRARY
sys.path.append( os.path.join( os.path.dirname( __file__ ), 
                               "../BLOCK0_DATA_CURATION" ) )
sys.path.append( os.path.join( os.path.dirname( __file__ ), 
                               "../BLOCK1_DATA_PROCESSING" ) )

import DATA_CURATION_LIB   as curate
import DATA_PROCESSING_LIB as process
from DATA_PROCESSING_LIB import STOP_WORDS

class OUTPUT_REPORTER:
    '''[BRIEF]: Class for reporting outputs and interacting with a GUI'''

    ENABLE_HEADERS    = True
    ENABLE_FIRSTLINES = True
    SCORE_THRESHOLD   = 0
    RESULT_DIR        = "."
    SAVE_IMAGES       = True

    def __init__( self,
                  ENABLE_HEADERS    = True,
                  ENABLE_FIRSTLINES = True,
                  SCORE_THRESHOLD   = 0,
                  RESULT_DIR        = ".",
                  SAVE_IMAGES       = True ):
        '''[BRIEF]: Initialize an OUTPUT_REPORTER object to report summarized text'''

        self.ENABLE_HEADERS    = ENABLE_HEADERS
        self.ENABLE_FIRSTLINES = ENABLE_FIRSTLINES
        self.SCORE_THRESHOLD   = SCORE_THRESHOLD
        self.RESULT_DIR        = "."
        self.SAVE_IMAGES       = SAVE_IMAGES
    
    def CONSTRUCT_SUMMARY( self,
                           PARSED_DATA_OBJ = None, 
                           SENTENCE_SCORES = None,
                           IMAGE_SIZE = (),
                           SOURCE_URL = "" ):

        '''[BRIEF]: COnstruct a summary of the text input based on initialized params'''

        
        with open( os.path.join( self.RESULT_DIR,"ARTICLE_SUMMARY.txt" ), 'w' ) as fPtr:
            
            HEADER_INFO = ''
            
            # TEXTUAL SUMMARY
            fPtr.write( "ARTICLE SUMMARY FOR URL: " + SOURCE_URL + "\n"   )
            fPtr.write( "DATE : " + datetime.datetime.now().strftime("%m_%d_%Y" ) + "\n\n" )

            if( self.ENABLE_HEADERS ):
                for level in range( 1, PARSED_DATA_OBJ.HEADER_MAXDEPTH+1 ):
                    
                    HEADER_KEY  = 'h'+str(level)
                    
                    if( PARSED_DATA_OBJ.HEADERS[ HEADER_KEY ] ):

                        fPtr.write( "HEADER "+str( level )+":"+"\n" )
                        HEADER_INFO = PARSED_DATA_OBJ.HEADERS[ HEADER_KEY ]             
                        fPtr.write( HEADER_INFO+"\n\n" )
            
            fPtr.write( "SUMMARY OF TEXT:"+"\n" )
            for sentence_tuple in SENTENCE_SCORES:
                if sentence_tuple[ 0 ] >= self.SCORE_THRESHOLD:
                    fPtr.write( sentence_tuple[1]+"\n" )

        # IMAGE EXTRACTION
        if( self.SAVE_IMAGES ):
            
            IMG_SIZES = []

            for link in PARSED_DATA_OBJ.IMAGE_LINKS:

                imgData = requests.get( link ).content
                try:
                    width, height = Image.open( BytesIO( imgData ) ).size 
                except OSError:
                    continue

                IMG_SIZES.append( width * height )
    
            maxSizeIdx = np.argmax( IMG_SIZES )
            
            try:
                pdb.set_trace()
                opener = urllib.request.URLopener()
                opener.addheader( 'User-Agent', 'Batman' )
                filename, headers = opener.retrieve( PARSED_DATA_OBJ.IMAGE_LINKS[ maxSizeIdx ],
                                                     os.path.join( self.RESULT_DIR, "ArticleThumb.jpg") )
                
                rawImage   = Image.open( os.path.join( self.RESULT_DIR, "ArticleThumb.jpg" ) )    
                resizedImg = rawImage.resize( IMAGE_SIZE, Image.ANTIALIAS )
                resizedImg.save( os.path.join( self.RESULT_DIR, "ArticleThumb.jpg" ) )
            except:
                pass

if( __name__ == "__main__" ):
    '''[BRIEF]: Sanity check for blocks from data curation to reporting'''

    # BLOCK0: DATA CURATION
    myData   = curate.DATA_CURATER( HEADER_MAXDEPTH = 3, PARSE_IMAGES = True )
    TEST_URL = input( "Enter URL for test ( Uses default URL if blank ): " ) 

    if not TEST_URL:
        TEST_URL = "https://getpocket.com/explore/item/home-sweet-homer-the-strange-saga-of-the-real-life-simpsons-house-in-nevada?utm_source=pocket-newtab"
    
    myData.SCRAPE_URL( SOURCE_URL = TEST_URL )

    # BLOCK1: DATA PROCESSING
    myProcessor = process.DATA_PROCESSOR( WORD_BLACKLIST = STOP_WORDS )
    myProcessor.WORDS_TOKENIZE( RAW_TEXT = ''.join( myData.PARAGRAPHS ) )
    myProcessor.SCORE_WORDS()
    myProcessor.SCORE_SENTENCES( PARAGRAPHS = myData.PARAGRAPHS )
    
    # BLOCK2: RESULT REPORTINGs
    myReport = OUTPUT_REPORTER( SCORE_THRESHOLD = np.nanmean( [ score[0] for score in myProcessor.SENTENCE_SCORES ] ),
                                SAVE_IMAGES = myData.PARSE_IMAGES )
    
    myReport.CONSTRUCT_SUMMARY( PARSED_DATA_OBJ = myData,
                                SENTENCE_SCORES = myProcessor.SENTENCE_SCORES,
                                SOURCE_URL = TEST_URL,
                                IMAGE_SIZE = ( 356, 280 ) )
