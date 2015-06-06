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
            print("State changed from: {} to {}".format(*args))
        yield self.subscribe(chirp_state, 'com.example.lpc00.state_change')

        def chirp_running(name):
            print ("Running command: {}".format(name))
        yield self.subscribe(chirp_running, 'com.example.lpc00.running_command')

        def chirp_ran(name):
            print ("Ran command: {}".format(name))
        yield self.subscribe(chirp_ran, 'com.example.lpc00.ran_command')

        returnValue(None)



if '__main__' == __name__:
    import sys
    extra = dict(token = sys.argv[1:] or "")
    
    runner = ApplicationRunner(url=u"ws://localhost:8080/ws", realm=u"realm1", extra=extra)
    runner.run(LpcQueries)
