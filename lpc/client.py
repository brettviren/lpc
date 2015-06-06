'''
Following:
https://github.com/tavendo/AutobahnPython/blob/master/examples/twisted/wamp/beginner/server.py
'''

import os

from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks, Deferred, returnValue
from autobahn.wamp.exception import ApplicationError
from autobahn.twisted.wamp import ApplicationSession,  ApplicationRunner

class LpcQueries(ApplicationSession):

    @inlineCallbacks
    def onJoin(self, details):
        
        def chirp_state(*args):
            print('chirp_state("%s")' % str(args))
            #print("State changed from: {} to {}".format(old, new))
        yield self.subscribe(chirp_state, 'com.example.lpc00.state_change')

        token = self.config.extra.get('token') or [""]
        token = token[0]
        print ('Using token: "%s"' % token)

        res = yield self.call('com.example.lpc00.get_state')
        print ('Got initial state: {}'.format(res))

        yield reactor.callLater(0, self.call, 'com.example.lpc00.display_token')
        yield reactor.callLater(1, self.call, 'com.example.lpc00.inroom.undisplay_token')

        res = yield self.call('com.example.lpc00.get_state')
        print ('Got state: {}'.format(res))

        res = yield self.call('com.example.lpc00.inroom.undisplay_token')
        print ('Undisplay token: {}'.format(res))

        if token:
            res = yield self.call('com.example.lpc00.inroom.vnc_server', 
                                  "secret", timeout=120)
            print ('Got vnc_server response: {}'.format(res))

        # res = yield self.call('com.example.lpc00.shutdown')
        # print ('Got shutdown: {}'.format(res))
        returnValue(None)



if '__main__' == __name__:
    import sys
    extra = dict(token = sys.argv[1:] or "")
    
    runner = ApplicationRunner(url=u"ws://localhost:8080/ws", realm=u"realm1", extra=extra)
    runner.run(LpcQueries)
