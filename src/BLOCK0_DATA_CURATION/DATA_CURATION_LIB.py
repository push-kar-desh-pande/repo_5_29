##
# @file   : DATA_CURATION_LIB.py 
# @brief  : Library with classes and functions for data curation
# @author : srijeshs
# @date   : 4/4/2020

# TODO: Move some of these to a common header module
# TODO: Add logging where appropriate
import os, sys
import selenium
import requests
import logging
import pdb

from bs4      import BeautifulSoup as bsoup
from selenium import webdriver
from selenium import webdriver

from selenium.common.exceptions import SessionNotCreatedException


sys.path.append( '/usr/local/bin' )


class DATA_CURATER:
    '''[BRIEF] : Class for the data scraping and cleaning block'''
    
    # BACKEND DEFINITIONS
    REQUEST_BACKEND = "requests"
    PARSER_BACKEND  = "bs4"
    PARSE_IMAGES    = True

    # DATA STRUCTURES AND PARAMS TO PASS ON TO CONSUMER BLOCKS    
    PARAGRAPHS  = []
    IMAGE_LINKS = []  
 
    def __init__( self, 
                  REQUEST_BACKEND = "requests",
                  PARSER_BACKEND  = "bs4",
                  PARSE_IMAGES    = True,
                  HEADER_MAXDEPTH = 6
                ):
        '''[BRIEF] : Initialize the DATA_OBJECT specifying request and parser preferences.
           [NOTE]  : Defaults to requests and bs4 with a header max depth of 6 (i.e.) h1 - h6.
        '''
        
        self.REQUEST_BACKEND = REQUEST_BACKEND
        self.PARSER_BACKEND  = PARSER_BACKEND        
        self.PARSE_IMAGES    = PARSE_IMAGES
        self.HEADER_MAXDEPTH = HEADER_MAXDEPTH
        self.HEADERS = { 'h1':[] }
        
        if( HEADER_MAXDEPTH > 1 ):
            for iLevel in range( 2, HEADER_MAXDEPTH+1 ):
                    keyVal = 'h' + str( iLevel )
                    self.HEADERS[ keyVal ] = []
    
    
    def MAKE_REQUEST( self,
                      SOURCE_URL = "",
                      URL_PARAMS = None   
                    ):
        '''[BRIEF]: Attempts to make a GET request to the specified URL with the corresponding params
        '''
        r = None
        
        '''
        [BRIEF] : Defining get selenium source function which used Selenium along with 4 versions of Chrome Drivers.
        More Versions of Chrome Drivers/ Firefox Drivers can be added to include multiple browsers and their versions
        '''
        def GET_SELENIUM_SOURCE(URL, IND = 0):
            driver_versions = ['chromedriver84.exe','chromedriver83.exe','chromedriver81.exe','chromedriver80.exe']
            try:
                chrome_path = driver_versions[IND]
                driver = webdriver.Chrome(chrome_path)
                driver.get(URL)
                page_src = driver.page_source
                return page_src
            except SessionNotCreatedException:
                if len(driver_versions) == IND + 1:
                    raise Exception('Chrome Browser Version Does Not Support any of the Listed Chrome Drivers') 
                else:
                    logging.debug("[DEBUG]: Trying The Next Chromvdriver version: "+driver_versions[IND + 1])
                    return GET_SELENIUM_SOURCE(URL, IND + 1)

        
        if( self.REQUEST_BACKEND == "requests" ):
            try:
                r = requests.get( SOURCE_URL, params = URL_PARAMS )
            except requests.exceptions.Timeout:
                logging.debug( "[DEBUG]: Request timed out in MAKE_REQUEST() with URL:"+
                               SOURCE_URL+
                               " PARAMS:"+
                               URL_PARAMS )
                pass
                                
            except requests.exceptions.TooManyRedirects:
                logging.debug( "[DEBUG]: Too many redirects in MAKE_REQUEST() with URL:"+
                               SOURCE_URL+
                               " PARAMS:"+
                               URL_PARAMS )
                pass
            
            except requests.exceptions.RequestException as e:
                logging.debug( "[DEBUG]: Request Exception in MAKE_REQUEST() with URL:"+
                               SOURCE_URL+
                               " PARAMS:"+
                               URL_PARAMS )
                pass
        
        # FIXME: Else use selenium as the backend. Fix this path
        else:
            r = GET_SELENIUM_SOURCE(SOURCE_URL)
        return r
    
    def SCRAPE_URL( self, 
                   SOURCE_URL = "",   # URL to scrape
                   URL_PARAMS = None, # Additional params to pass with GET request
                   PARA_MINLEN = 15   # Paragraph elements < PARA_MINLEN characters will be ignored
                  ):
        '''[BRIEF] : Function requests the source of the specified URL and scrapes the title, headers and paragraph elements of the HTML page
           [NOTE]  : All paragraphs < PARA_MINLEN characters in length are ignored ( default = 15 )
        '''        

        # [STEP 1]: RAW CONTENT PROCUREMENT
        rawContent = self.MAKE_REQUEST( SOURCE_URL, URL_PARAMS )

        # [STEP 2]: USING PARSER TO GET HEADERS AND PARAGRAPHS
        # FIXME: For now, bs4 is the only supported parser backend
        if( self.PARSER_BACKEND == "bs4" ):
            soup = bsoup( rawContent.content, 'html.parser' )

            # STORE HEADERS AT EACH LEVEL
            for iHeaderLvl in range( self.HEADER_MAXDEPTH ):                   
                headerKey = 'h' + str( iHeaderLvl )

                for item in soup.find_all( headerKey ):
                    try:
                        item.get_text()
                        self.HEADERS[ headerKey ] = item.get_text()
                    except:
                        print( 'Unable to extract text from bs4 HEADER object' )
                        logging.error('Unable to extract text from bs4 HEADER object')

            # STORE PARAGRAPHS
            for iPara in soup.find_all( 'p' ):
                if( iPara.get_text() ):
                    if ( len( iPara.get_text().strip() ) >= PARA_MINLEN ):
                        self.PARAGRAPHS.append( iPara.get_text().strip() )
			
			# STORE IMAGE LINKS
            if( self.PARSE_IMAGES ):
                soup = bsoup( rawContent.text, 'lxml' )
                images = soup.find_all( 'img' )
                self.IMAGE_LINKS = [ link.get( 'src' ) for link in images ]
                self.IMAGE_LINKS = [ valid_link for valid_link in self.IMAGE_LINKS if valid_link ]
        return

if( __name__ == "__main__" ):
    '''Sanity for this module by scraping a sample article'''

    myData = DATA_CURATER( HEADER_MAXDEPTH=3, REQUEST_BACKEND="requests" )
    TEST_URL = input( "Enter URL for test ( Uses default URL if blank ): " )

    if not TEST_URL:
        TEST_URL = "https://getpocket.com/explore/item/home-sweet-homer-the-strange-saga-of-the-real-life-simpsons-house-in-nevada?utm_source=pocket-newtab"

    myData.SCRAPE_URL( SOURCE_URL = TEST_URL )
    print( "First two paragraphs: ", myData.PARAGRAPHS[ :2 ] )
