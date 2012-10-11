#!/usr/bin/env python
from __future__ import print_function
import sys
from twisted.internet import reactor
from twisted.web.client import Agent
from twisted.web.http_headers import Headers
from twisted.internet.protocol import Protocol
from bs4 import BeautifulSoup
from twisted.internet.ssl import ClientContextFactory
from urlparse import urlparse

def host(url): return urlparse(url).hostname

outstandingrequests = []

results = {} #global, for now

agent = Agent(reactor)

class PageBodyParser(Protocol):
    def __init__(self, url):
        self.url = url
        self.buffer = ""
    def dataReceived(self, data):
        self.buffer += data
    def connectionLost(self, reason):
        global outstandingrequests, hostname
        # Using beautifulsoup, so we'll still try and parse a page even if we got an error
        soup = BeautifulSoup(self.buffer)
        results[self.url] = True
        newUrls = [link.get('href') for link in soup.find_all('a')]
        [makeRequest(url) for url in newUrls if hostname == host(url) and (not url in outstandingrequests) and (not url in results) and (not urlparse(url).params)]
        outstandingrequests.remove(self.url)
        if(not outstandingrequests): reactor.stop() 
        else: print(outstandingrequests)

def handleResponse(response, url):
    if(301 == response.code):
        #XXX: This appears to be the correct way to get a header from the response, but it's ugly as hell
        outstandingrequests.remove(url)
        makeRequest(response.headers.getRawHeaders('Location')[0])
    else:
        response.deliverBody(PageBodyParser(url))

def makeRequest(url):
    global outstandingrequests
    request = agent.request('GET', url)
    request.addCallback(handleResponse, url)
    outstandingrequests.append(url)
    return request

if('__main__' == __name__):
    global hostname
    hostname = host(sys.argv[1])
    makeRequest(sys.argv[1])
    reactor.run()
    print(results)
