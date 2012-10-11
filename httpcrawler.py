#!/usr/bin/env python
from __future__ import print_function
import sys
from twisted.internet import reactor
from twisted.web.client import Agent
from twisted.web.http_headers import Headers
from twisted.internet.protocol import Protocol
from bs4 import BeautifulSoup
from twisted.internet.ssl import ClientContextFactory
from urlparse import urlparse, urljoin, urlsplit, urlunsplit
from pygraphviz import *

def host(url): return urlparse(url).hostname
def strip(url):
    split = list(urlsplit(url))
    split[4]=''
    return urlunsplit(split)

outstandingrequests = []

results = {} #global, for now

agent = Agent(reactor)

class PageResult:
    def __init__(self, url, body):
        self.url = url
        soup = BeautifulSoup(body)
        alllinks = [strip(urljoin(url,link.get('href'))).encode('utf8') for link in soup.find_all('a')]
        self.links = set([url for url in alllinks if hostname == host(url)])
        self.images = [urljoin(url, image.get('src')).encode('utf8') for image in soup.find_all('img') if image.get('src')]
        self.css = [urljoin(url, link.get('href')).encode('utf8') for link in soup.find_all('link') if u'stylesheet' == link.get('rel')]
        self.js = [urljoin(url, script.get('src')).encode('utf8') for script in soup.find_all('script') if script.get('src')]
    def addSelfTo(self, graph):
        graph.add_node(self.url)
        for l in self.links:
            graph.add_edge(self.url, l)

class RedirectResult:
    def __init__(self, url, redirect):
        self.url = url
        self.outgoinglinks = [redirect]
    def addSelfTo(self, graph): pass

class PageBodyParser(Protocol):
    def __init__(self, url):
        self.url = url
        self.buffer = ""
    def dataReceived(self, data):
        self.buffer += data
    def connectionLost(self, reason):
        global outstandingrequests, hostname
        # Using beautifulsoup, so we'll still try and parse a page even if we got an error
        result = PageResult(self.url, self.buffer)
        results[self.url] = result
        [makeRequest(url) for url in result.links if
            (not url in outstandingrequests) and (not url in results) and (not urlparse(url).query)]
        outstandingrequests.remove(self.url)
        if(not outstandingrequests): reactor.stop() 
        else: print("Outstanding requests: %s" % outstandingrequests)

def handleResponse(response, url):
    if(301 == response.code):
        #XXX: This appears to be the correct way to get a header from the response, but it's ugly as hell
        redirect = response.headers.getRawHeaders('Location')[0]
        results[url] = RedirectResult(url, redirect)
        outstandingrequests.remove(url)
        makeRequest(redirect)
    else:
        response.deliverBody(PageBodyParser(url))

def makeRequest(url):
    global outstandingrequests
    print("Requesting %s" % url)
    request = agent.request('GET', url)
    request.addCallback(handleResponse, url)
    outstandingrequests.append(url)
    return request

if('__main__' == __name__):
    global hostname
    hostname = host(sys.argv[1])
    makeRequest(sys.argv[1])
    reactor.run()
    graph = AGraph(directed=True, overlap='scale')
    for v in results.itervalues():
        v.addSelfTo(graph)
    graph.draw('out.ps', prog='neato')

