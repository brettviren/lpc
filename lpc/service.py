'''
Following:
https://github.com/tavendo/AutobahnPython/blob/master/examples/twisted/wamp/beginner/server.py
'''

import os
import random
import subprocess
from exceptions import OSError

from twisted.internet.defer import inlineCallbacks, returnValue
from autobahn.twisted.wamp import ApplicationSession

class LpcCommands(ApplicationSession):
    '''
    A WAMP client providing Callee for LPC commands and a Publisher exposing state changes.
    '''
    @inlineCallbacks
    def onJoin(self, details):
        
        name = self.config.extra.get('name', os.environ.get('LPC_NAME', 'lpc'))
        domain = self.config.extra.get('domain', os.environ.get('LPC_DOMAIN', 'gov.bnl.phy'))
        self._uripat = u'%s.%s.%%s' % (domain, name)

        self.state = 'OFF'
        self.token_display_proc = None
        self.renew_token()

        self.register_command('get_state',       self.get_state,      False, None, None)
        self.register_command('display_token',   self.display_token,  False, 'IDLE', 'TOKEN')
        self.register_command('undisplay_token', self.undisplay_token, True, 'TOKEN', 'IDLE')


        # Register our commands to do things on the system
        import commands
        for methname in dir(commands):
            if not methname.startswith('cmd_'):
                continue
            meth = getattr(commands, methname)
            
            name = getattr(meth, 'name', methname[4:])
            need_token = getattr(meth, 'token', True)
            from_state = getattr(meth, 'from_state', 'IDLE')
            to_state = getattr(meth, 'to_state', 'ACTIVE')

            yield self.register_command(name, meth, need_token, from_state, to_state)

        self.set_state('IDLE')
        returnValue("joined")

    def register_command(self, name, meth, need_token=True, from_state='IDLE', to_state='ACTIVE'):
        '''
        Register method <meth> under command named <name> with state constraints.
        '''
        
        if need_token:
            name = 'inroom.' + name
        uri = self.uri(name)
        caller = lambda *a, **k: self.do_command(name, meth, from_state, to_state, *a, **k)
        print("registering: {} {}->{}".format(uri,from_state,to_state))
        return self.register(caller, uri)


    def do_command(self, name, meth, from_state, to_state, *args, **kwds):
        '''
        Run the named command.
        '''
        if from_state and self.state != from_state:
            return 'Can not run command "%s" while in state %s' % (name, self.state)
        if to_state:
            self.set_state(to_state)
        self.publish(self.uri('running_command'), name)
        print ('Running "%s"' % name)
        ret = meth(*args, **kwds)
        print ('Command "%s" return "%s"' % (name, str(ret)))
        self.publish(self.uri('ran_command'), name)
        if from_state:
            self.set_state(from_state) # fixme: currently assume we go back to initial state
        return ret

    def uri(self, name):
        return self._uripat % name

    def renew_token(self):
        '''
        Make a new room token.
        '''
        self.token = ''.join([str(random.randint(0,9)) for ind in range(4)])
        print ('ROOM TOKEN: %s' % self.token)
        self.publish(self.uri('token'), self.token)
        return

    @inlineCallbacks
    def display_token(self):
        '''
        Display the token
        '''
        self.undisplay_token()

        cmd="zenity --info --text={} --timeout=300".format(self.token)
        self.token_display_proc = subprocess.Popen(cmd, shell=True)
        rc = yield self.token_display_proc.wait()
        returnValue(rc)

    @inlineCallbacks
    def undisplay_token(self):
        if self.token_display_proc and self.token_display_proc.returncode == None:
            print ("Undisplay token: terminating PID %d" % self.token_display_proc.pid)
            try:
                yield self.token_display_proc.terminate()
            except OSError, e:
                print ('Warning: failed to terminate token display: "%s"' % e)
                pass
        if self.token_display_proc and self.token_display_proc.returncode == None:
            print ("Undisplay token: killing PID %d" % self.token_display_proc.pid)
            try:
                yield self.token_display_proc.kill() # it's dead, Jim
            except OSError, e:
                print ('Warning: failed to kill token display: "%s"' % e)
                pass

        self.token_display_proc = None
        returnValue(None)

    def set_state(self, state):
        '''
        Unconditionally set the state to <state> and Publish.
        '''
        oldstate = self.state
        self.state = state
        print ('Setting state from "%s" --> "%s"' % (oldstate, state))
        self.publish(self.uri('state_change'), oldstate, state)


    # is this needed?  Does WAMP cache last published 'state_change'?
    def get_state(self):
        '''
        Return the current LPC state.
        '''
        print ('Returning state: %s' % self.state)
        return self.state


    def shutdown(self):
        '''
        Shutdown the service
        '''
        self.set_state("OFFLINE")
        #from twisted.internet import reactor
        #reactor.stop()



if '__main__' == __name__:
    from autobahn.twisted.wamp import ApplicationRunner
    extra = dict(name='lpc00', domain='com.example')
    runner = ApplicationRunner(url=u"ws://localhost:8080/ws", realm=u"realm1", extra=extra,
                               debug = False, debug_wamp = False, debug_app = True)
    runner.run(LpcCommands)
