'''The commands the LPC implements.

Each command is a callable object named starting with "cmd_".

A command is allowed and encouraged to block.

Each command object may have these optional data elements:

 - name :: the command name used in forming the WAMP URI.  If not
   specified the object name is used with "cmd_" removed.

 - from_state :: the state the LPC must be in for this command to be
   run, defaults to "IDLE".

 - to_state :: the state the LPC will enter on calling this command,
   defaults to "ACTIVE"

 - token :: set to False if no room token is needed, default is true.

'''
import subprocess

def cmd_vnc_server(password="", timeout=60):
    '''
    Start a VNC server on the LPC accepting the given password at least until reaching the timeout.
    '''
    cmd = "x11vnc -display :0 -once -timeout {} -passwd {}".format(timeout,password)
    proc = subprocess.Popen(cmd, shell=True)
    return proc.wait()


    


