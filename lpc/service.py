'''
Following:
https://github.com/tavendo/AutobahnPython/blob/master/examples/twisted/wamp/beginner/server.py
'''

import os
import random

from twisted.internet.defer import inlineCallbacks
from autobahn.wamp.exception import ApplicationError
from autobahn.twisted.wamp import ApplicationSession

class LpcCommands(ApplicationSession):
    '''
    A WAMP client providing Callee for LPC commands and a Publisher exposing state changes.
    '''

    # https://github.com/crossbario/crossbarexamples/blob/master/userconfig/python/component.py
    # if not using crossbar, config needs:
    #https://github.com/crossbario/crossbarexamples/blob/master/userconfig/python/component.py#L11

    @inlineCallbacks
    def onJoin(self, details):
        
        self.state = 'OFF'
        self.renew_token()

        # fixme: is self.config.extra a dict?
        name = self.config.extra.get('name', os.environ.get('LPC_NAME', 'lpc'))
        domain = self.config.extra.get('domain', os.environ.get('LPC_DOMAIN', 'gov.bnl.phy'))
        self._uripat = u'%s.%s.%%s' % (domain, name)

        yield self.register(self.get_state, self.uri(u'get_state'))
        #yield self.register(self.shutdown, self.uri(u'shutdown'))

        import commands
        for methname in dir(commands):
            if not methname.startswith('cmd_'):
                continue
            cmdname = methname[4:]
            meth = getattr(commands, methname)
            if not meth:
                raise ApplicationError('Failed to find command "{}"'.format(cmdname))
                
            if hasattr(meth,'token') and meth.token:
                caller = lambda token, *a, **k: self.do_room_command(token, cmdname, meth, *a, **k)
            else:
                caller = lambda *a, **k: self.do_command(cmdname, meth, *a, **k)

            try:
                yield self.register(caller, self.uri(cmdname))
            except Exception as e:
                print("failed to register procedure {}: {}".format(cmdname, e))
            else:
                print("procedure registered: {}".format(cmdname))

        self.set_state('IDLE')


    def uri(self, name):
        return self._uripat % name

    def renew_token(self):
        '''
        Make a new room token.
        '''
        self.token = ''.join([str(random.randint(0,10)) for ind in range(4)])
        print ('ROOM TOKEN: %s' % self.token)
        return
        

    def set_state(self, state):
        '''
        Unconditionally set the state to <state> and Publish.
        '''
        oldstate = self.state
        self.state = state
        self.publish(self.uri('state_change'), oldstate, state)

    def get_state(self):
        '''
        Return the current LPC state.
        '''
        return self.state

    def shutdown(self):
        '''
        Shutdown the service
        '''
        self.set_state("OFFLINE")
        #from twisted.internet import reactor
        #reactor.stop()

    def do_room_command(self, token, name, meth, *args, **kwds):
        if token != self.token:
            return 'Incorrect room token'
        return self.do_command(name, meth, *args, **kwds)

    def do_command(self, name, meth, *args, **kwds):
        '''
        Run the named command.
        '''
        if self.state != "IDLE":
            raise ApplicationError('Can not run command "%s" in state %s' % self.state)

        self.set_state('ACTIVE')
        self.publish(self.uri('running_command'), name)
        ret = meth(*args, **kwds)
        self.publish(self.uri('ran_command'), name)
        return ret
    

if '__main__' == __name__:
    from autobahn.twisted.wamp import ApplicationRunner
    extra = dict(name='lpc00', domain='com.example')
    runner = ApplicationRunner(url=u"ws://localhost:8080/ws", realm=u"realm1", extra=extra,
                               debug = False, debug_wamp = True, debug_app = True)
    runner.run(LpcCommands)
