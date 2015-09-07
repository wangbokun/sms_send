# -*- coding: utf-8 -*- 
import time
import sys
import os
import subprocess
import errno
import re

PIPE = subprocess.PIPE

if subprocess.mswindows:
    from win32file import ReadFile, WriteFile
    from win32pipe import PeekNamedPipe
    import msvcrt
else:
    import select
    import fcntl

class Popen(subprocess.Popen):
    def recv(self, maxsize=None):
        return self._recv('stdout', maxsize)

    def recv_err(self, maxsize=None):
        return self._recv('stderr', maxsize)

    def send_recv(self, input='', maxsize=None):
        return self.send(input), self.recv(maxsize), self.recv_err(maxsize)

    def get_conn_maxsize(self, which, maxsize):
        if maxsize is None:
            maxsize = 1024
        elif maxsize < 1:
            maxsize = 1
        return getattr(self, which), maxsize

    def _close(self, which):
        getattr(self, which).close()
        setattr(self, which, None)

    if subprocess.mswindows:
        def send(self, input):
            if not self.stdin:
                return None

            try:
                x = msvcrt.get_osfhandle(self.stdin.fileno())
                (errCode, written) = WriteFile(x, input)
            except ValueError:
                return self._close('stdin')
            except (subprocess.pywintypes.error, Exception), why:
                if why[0] in (109, errno.ESHUTDOWN):
                    return self._close('stdin')
                raise

            return written

        def _recv(self, which, maxsize):
            conn, maxsize = self.get_conn_maxsize(which, maxsize)
            if conn is None:
                return None

            try:
                x = msvcrt.get_osfhandle(conn.fileno())
                (read, nAvail, nMessage) = PeekNamedPipe(x, 0)
                if maxsize < nAvail:
                    nAvail = maxsize
                if nAvail > 0:
                    (errCode, read) = ReadFile(x, nAvail, None)
            except ValueError:
                return self._close(which)
            except (subprocess.pywintypes.error, Exception), why:
                if why[0] in (109, errno.ESHUTDOWN):
                    return self._close(which)
                raise

            if self.universal_newlines:
                read = self._translate_newlines(read)
            return read

    else:
        def send(self, input):
            if not self.stdin:
                return None

            if not select.select([], [self.stdin], [], 0)[1]:
                return 0

            try:
                written = os.write(self.stdin.fileno(), input)
            except OSError, why:
                if why[0] == errno.EPIPE: #broken pipe
                    return self._close('stdin')
                raise

            return written

        def _recv(self, which, maxsize):
            conn, maxsize = self.get_conn_maxsize(which, maxsize)
            if conn is None:
                return None

            flags = fcntl.fcntl(conn, fcntl.F_GETFL)
            if not conn.closed:
                fcntl.fcntl(conn, fcntl.F_SETFL, flags| os.O_NONBLOCK)

            try:
                if not select.select([conn], [], [], 0)[0]:
                    return ''

                r = conn.read(maxsize)
                if not r:
                    return self._close(which)

                if self.universal_newlines:
                    r = self._translate_newlines(r)
                return r
            finally:
                if not conn.closed:
                    fcntl.fcntl(conn, fcntl.F_SETFL, flags)

    @staticmethod
    def recv_some(p, t=.1, e=1, tr=5, stderr=0):
        if tr < 1:
            tr = 1
        x = time.time()+t
        y = []
        r = ''
        pr = p.recv
        if stderr:
            pr = p.recv_err
        while time.time() < x or r:
            r = pr()
            if r is None:
                if e:
                    raise Exception("Other end disconnected!")
                else:
                    break
            elif r:
                #return r
                y.append(r)
                #print(r)
            else:
                #time.sleep(0.2)
                time.sleep(max((x-time.time())/tr, 0))
        return ''.join(y)

    @staticmethod
    def send_all(p, data):
        while len(data):
            sent = p.send(data)
            if sent is None:
                raise Exception("Other end disconnected!")
            data = buffer(data, sent)

    @staticmethod
    def recv_some_restring(p, prog, t=.1, e=1, tr=5, stderr=0):
        if tr < 1:
            tr = 1
        x = time.time()+t
        y = []
        r = ''
        pr = p.recv
        if stderr:
            pr = p.recv_err
        while time.time() < x or r:
            r = pr()
            if r is None:
                if e:
                    raise Exception(e)
                else:
                    break
            elif r:
                y.append(r)
                # print y
                result = prog.search(''.join(y))
                if result:
                    print '<>'
                    break
            else:
                time.sleep(max((x-time.time())/tr, 0))
        return ''.join(y)


# class RunCmd(threading.Thread):
    # def __init__(self, cmd, timeout):
        # import threading
        # threading.Thread.__init__(self)
        # self.cmd = cmd
        # self.timeout = timeout

    # def run(self):
        # self.p = subprocess.Popen(self.cmd)
        # self.p.wait()

    # def Run(self):
        # self.start()
        # self.join(self.timeout)

        # if self.is_alive():
            # self.p.terminate()
            # self.join()

# RunCmd(["./someProg", "arg1"], 60).Run()

def do_cmd(cmd, out_func = None, break_flag = None):
    import sys
    if out_func == None:
        
        out_func = sys.stdout.write
    if break_flag == None:
        break_flag = False

    if sys.platform == 'win32':
        print 'in win32 executing'
        cmds = cmd.split(" ")
        print cmds
        p = Popen(cmd, stdin=PIPE, stdout=PIPE,
                         stderr=PIPE,
                         shell=True)
    else:
        p = Popen(cmd,stdin=PIPE, stdout=PIPE,
                         stderr=PIPE,
                         shell=True)
    ret = ''
    err = None
    while True:
        err = None
        buff = p.recv_err()
        isErr = False
        
        if buff == "" or buff == None:
            buff = Popen.recv_some(p, e=0)
        else:
            isErr = True
            
        
        if len(buff) > 1:
            
            out_func(buff)
        if break_flag:
            out_func("break by ctrl")
            p.terminate()
            
        if p.poll() != None:
            ret += ' ret_code:' + str(p.returncode)
            break
    out_func("end cmd")
    
def do_cmd_thread(*nargs, **nkwargs):
    import threading, time
    
    t = threading.Thread(target = do_cmd, args = nargs)
    t.start()
    return t
    
    
if __name__ == "__main__":
    def out_func(msg):
        print("info:" + msg)
    flag = False
    
    do_cmd_thread("D:\\file\\cloudil\\pyadmin\\code\\imgr\\instmgt\\ext\\pscp -pw 235711 D:\\file\\cloudil\\pyadmin\\code\\imgr\\servicelocator.py root@172.16.40.145:/tmp/hostinfo_1367051772.38.py", out_func, flag)
    import time
    while 1:
        time.sleep(0.5)