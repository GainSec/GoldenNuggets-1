from burp import IBurpExtender, IContextMenuFactory
from java.util import ArrayList
from javax.swing import JMenuItem
import threading
import sys
#Burp Plug-In that parses sitemap for URI wordlist - Param Wordlist - Post Request Data - Interesting Headers
#v0.3 Writes URI and URI Param Wordlist
#To Do: Post Request Data and Interesting Headers
#Created by GainSec; Shoutout to Th3W1zard for help
#Make sure to change File location for output
try:
    from exceptions_fix import FixBurpExceptions
except ImportError:
    pass    

class BurpExtender(IBurpExtender, IContextMenuFactory):
    def registerExtenderCallbacks(self, callbacks):
        
        sys.stdout = callbacks.getStdout()
        self.callbacks = callbacks
        self.helpers = callbacks.getHelpers()
        self.callbacks.setExtensionName("Gold-Nuggets-TreeHouse-WL")
        callbacks.registerContextMenuFactory(self)
        
        return

    def createMenuItems(self, invocation):
        self.context = invocation
        menuList = ArrayList()
        menuItem = JMenuItem("URI Nuggets from Selected",
                              actionPerformed=self.createWordlistFromSelected)
        menuList.add(menuItem)
        menuItem = JMenuItem("URI Nuggets from Scope",
                              actionPerformed=self.createWordlistFromScope)
        menuList.add(menuItem)
        menuItem = JMenuItem("URI Param Nuggets from Scope", 
        					  actionPerformed=self.createParamlistFromSelected)

        menuList.add(menuItem)
        return menuList

    def createWordlistFromSelected(self, event):
        self.fromScope = False
        t = threading.Thread(target=self.createWordlist)
        t.daemon = True
        t.start()

    def createWordlistFromScope(self, event):
        self.fromScope = True
        t = threading.Thread(target=self.createWordlist)
        t.daemon = True
        t.start()

    def createParamlistFromSelected(self, event):
    	self.fromScope = True
    	t = threading.Thread(target=self.createParamlist)
    	t.daemon = True
    	t.start()

    def createParamlist(self):
    	httpTraffic = self.context.getSelectedMessages()
    	hostUrls = []
    	for traffic in httpTraffic:
    		try:
    			hostUrls.append(str(traffic.getUrl()))
    		except UnicodeEncodeError:
    			continue

    	urllist = []
    	siteMapData = self.callbacks.getSiteMap(None)
    	for entry in siteMapData:
    		requestInfo = self.helpers.analyzeRequest(entry)
    		url = requestInfo.getUrl()
    		try:
    			decodedUrl = self.helpers.urlDecode(str(url))
    		except Exception as e:
    			continue

    		if self.fromScope and self.callbacks.isInScope(url):
    			urllist.append(decodedUrl)
    		else:
    			for url in hostUrls:
    				if decodedUrl.startswith(str(url)):
    					urllist.append(decodedUrl)

    	filenamelist = []
    	for entry in urllist:
    		filenamelist.append(entry.split('?',3)[-1])

    	for word in sorted(set(filenamelist)):
            with open('/Users/xeno/Wordlists-Xeno/Custom/GoldNuggets-Param-WL.txt', 'a') as f:
                try:
                    print (word)
                    f.write(word +'\n')
                except UnicodeEncodeError:
                    continue

    def createWordlist(self):
        httpTraffic = self.context.getSelectedMessages()        
        hostUrls = []
        for traffic in httpTraffic:
            try:
                hostUrls.append(str(traffic.getUrl()))
            except UnicodeEncodeError:
                continue

        urllist = []
        siteMapData = self.callbacks.getSiteMap(None)
        for entry in siteMapData:
            requestInfo = self.helpers.analyzeRequest(entry)
            url = requestInfo.getUrl()
            try:
                decodedUrl = self.helpers.urlDecode(str(url))
            except Exception as e:
                continue

            if self.fromScope and self.callbacks.isInScope(url):
                urllist.append(decodedUrl)
            else:
                for url in hostUrls:
                    if decodedUrl.startswith(str(url)):
                        urllist.append(decodedUrl)
        
        filenamelist = []
        for entry in urllist:
            filenamelist.append(entry.split('/',3)[-1])

        for word in sorted(set(filenamelist)):
            if word:
                with open('/Users/xeno/Wordlists-Xeno/Custom/GoldNuggets-WL.txt', 'a') as f:
                    try:
                        print (word)
                        f.write(word +'\n')
                    except UnicodeEncodeError:
                        continue
try:
    FixBurpExceptions()
except:
    pass
