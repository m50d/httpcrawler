#!/usr/bin/env python
from __future__ import print_function
import sys
from twisted.internet import reactor
from twisted.web.client import Agent
from twisted.web.http_headers import Headers
from twisted.internet.protocol import Protocol
from bs4 import BeautifulSoup
from twisted.internet.ssl import ClientContextFactory

results = {} #global, for now

agent = Agent(reactor)

class PageBodyParser(Protocol):
    def __init__(self, url):
        self.url = url
        self.buffer = ""
    def dataReceived(self, data):
        self.buffer += data
    def connectionLost(self, reason):
        # Using beautifulsoup, so we'll still try and parse a page even if we got an error
        soup = BeautifulSoup(self.buffer)
        print(soup.prettify())
        

def handleResponse(response, url):
    if(301 == response.code):
        #XXX: This appears to be the correct way to get a header from the response, but it's ugly as hell
        otherdeferred = makeRequest(response.headers.getRawHeaders('Location')[0])
        print(otherdeferred)
        return otherdeferred
    else:
        response.deliverBody(PageBodyParser(url))

def makeRequest(url):
    request = agent.request('GET', url)
    request.addCallback(handleResponse, url)
    return request

if('__main__' == __name__):
    initialrequest = makeRequest(sys.argv[1])
    def cbShutdown(ignored):
        reactor.stop()
    initialrequest.addBoth(cbShutdown) 
    reactor.run()
    print(results)
