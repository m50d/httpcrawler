#!/usr/bin/env python
from __future__ import print_function
import sys
from twisted.internet import reactor
from twisted.web.client import Agent
from twisted.web.http_headers import Headers

results = {} #global, for now
agent = Agent(reactor)

if('__main__' == __name__):
    initialurl = sys.argv[1]
    initialrequest = agent.request('GET', initialurl)
    def cbResponse(ignored):
        print('Response received')
    initialrequest.addCallback(cbResponse)
    def cbShutdown(ignored):
        reactor.stop()
    initialrequest.addBoth(cbShutdown) 
    reactor.run()
    print(results)
