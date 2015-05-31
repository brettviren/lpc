'''
Following:
https://github.com/tavendo/AutobahnPython/blob/master/examples/twisted/wamp/beginner/server.py
'''

import os

from twisted.internet.defer import inlineCallbacks
from autobahn.wamp.exception import ApplicationError
from autobahn.twisted.wamp import ApplicationSession,  ApplicationRunner


class LpcQueries(ApplicationSession):

    @inlineCallbacks
    def onJoin(self, details):
        
        def chirp_state(old, new):
            print("State changed from: {} to {}".format(old, new))
        yield self.subscribe(chirp_state, 'com.example.lpc00.state_change')

        token = self.config.extra.get('token', os.environ.get('LPC_TOKEN', ''))


        res = yield self.call('com.example.lpc00.get_state')
        print ('Got state: {}'.format(res))

        res = yield self.call('com.example.lpc00.vnc_server', 
                              token, "secret", timeout=120)
        print ('Got vnc_server response: {}'.format(res))

        # res = yield self.call('com.example.lpc00.shutdown')
        # print ('Got shutdown: {}'.format(res))

        from twisted.internet import reactor
        reactor.stop()


if '__main__' == __name__:
    import sys
    extra = dict(token = sys.argv[1:] or "")
    
    runner = ApplicationRunner(url=u"ws://localhost:8080/ws", realm=u"realm1", extra=extra)
    runner.run(LpcQueries)
