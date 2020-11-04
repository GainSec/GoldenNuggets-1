from burp import IBurpExtender, IContextMenuFactory
from java.util import ArrayList
from javax.swing import JMenuItem
import threading
import sys
import os
import re
#v0.4 Writes URI, Single Word and URI Param Wordlist
#To Do: Post Request Data and Interesting Headers
#Created by GainSec; Shoutout to JosephRC for the help
try:
    from exceptions_fix import FixBurpExceptions
except ImportError:
    pass    

class BurpExtender(IBurpExtender, IContextMenuFactory):
    def __init__(self):
        self.urls = set()
        self.uris = set()
        self.params = set()
        self.words = set()

    def registerExtenderCallbacks(self, callbacks):
        sys.stdout = callbacks.getStdout()
        self.callbacks = callbacks
        self.helpers = callbacks.getHelpers()
        self.callbacks.setExtensionName("GoldenNuggets")
        callbacks.registerContextMenuFactory(self)
        return

    def createMenuItems(self, invocation):
        self.context = invocation
        menuList = ArrayList()
        menuItem = JMenuItem("Mine Dem Nuggets",
                              actionPerformed=self.createWordlistFromSelected)

        menuList.add(menuItem)
        return menuList

    def createWordlistFromSelected(self, event):
        self.fromScope = False
        t = threading.Thread(target=self.createWordlist)
        t.daemon = True
        t.start()


    def createWordlist(self):
        # print('test')
        uriList = []
        words = []
        # Create a list of hosts from the context       
        hostUrls = []
        # Create a unique Urls list
        urlList = []
        ##################################
        # Get URLs from Site Map / Traffic
        ##################################
        # Get the HTTP trffic from the Burp Context
        httpTraffic = self.context.getSelectedMessages() 
        # For each item in the http traffic
        for traffic in httpTraffic:
            # Try to append each host url to the Host Urls list
            try:
                hostUrls.append(str(traffic.getUrl()))
            except UnicodeEncodeError:
                continue
        # Grab the site map data from the context
        siteMapData = self.callbacks.getSiteMap(None)
        # For each entry in the site map data
        for entry in siteMapData:
            # Get the request info from the entry
            requestInfo = self.helpers.analyzeRequest(entry)
            # Get the url from the request info
            url = requestInfo.getUrl()
            # Try to decode the URL
            try:
                decodedUrl = self.helpers.urlDecode(str(url))
            except Exception as e:
                continue
            # For each url in the Host URLs list
            for url in hostUrls:
                # If the decoded URL matches the URL from the list
                if decodedUrl.startswith(str(url)):
                    # Append the decoded url to the URLs list
                    self.urls.add(decodedUrl)
        ##################
        # URIS
        # print('##########')
        # print('## URIS ##')
        # print('##########')
        for line in self.urls:
            x = line.split(line.split('/')[2])[-1]
            # print(x)
            self.uris.add(x)
        # # Now write to file
        with open(os.path.expanduser('~/gn_Uris.txt'), 'a') as f:
            for uri in self.uris:
                try:
                    f.write(uri+'\n')
                except:
                    pass
        # WORDLISTS
        # print('###########')
        # print('## WORDS ##')
        # print('###########')
        for uri in self.uris:
            for item in re.split('\W',uri):
                if item != '':
                    # print(item)
                    self.words.add(item)
        # Now write to file
        with open(os.path.expanduser('~/gn_Words.txt'), 'a') as f:
            for word in self.words:
                try:
                    f.write(word+'\n')
                except:
                    pass
        # PARAMS
        # print('############')
        # print('## PARAMS ##')
        # print('############')
        for uri in self.urls:
            param = uri.split('?')[-1]
            if '/' not in param and param != "":
                # print(ff)
                self.params.add(param)
        # Now write to file
        with open(os.path.expanduser('~/gn_Params.txt'), 'a') as f:
            for param in self.params:
                try:
                    f.write(param+'\n')
                except:
                    pass
        # THIS WORKS FOR REFERRENCE
        # with open(os.path.expanduser('~/gn_Uris.txt'), 'r') as f:
        #     for line in f:
        #         self.tempUris.append(line)
try:
    FixBurpExceptions()
except:
    pass
