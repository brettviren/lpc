'''
The commands the LPC implements.

Each command is referenced by the function name and may block.
'''
import subprocess

def cmd_vnc_server(password="", timeout=60):
    '''
    label = Start VNC Server
    auth = true
    command = x11vnc -display :0 -once -timeout {timeout} -passwd {vnc_password}
    help = Run "bvnc" or "vncviewer {lpc_host}" or your favorite VNC viewer.
    '''
    return "x11vnc -display :0 -once -timeout {} -passwd {}".format(timeout,password)
cmd_vnc_server.token = True

