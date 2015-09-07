
'''
zmq通讯模块

'''

import zmq
import json
import threading
import time

TIME_OUT = 5
class ZmqClientUtil():
    NODE_READY = "\x01"      # Signals worker is ready
    NODE_HEARTBEAT = "\x02"  # Signals worker heartbeat


    def __init__(self, con_str):
        self.context = zmq.Context()
        self.poll = zmq.Poller()
        self.client = self.init_channel(self.context, self.poll, con_str)
        self.con_str = con_str


    def recv(self):
        reply = None
        start_time = time.time()
        while 1:
            socks = dict(self.poll.poll(2))
            #print("recv...")
            if time.time() - start_time > TIME_OUT:
                break

            if socks.get(self.client) == zmq.POLLIN:
                reply = self.client.recv()
                break

        return reply

    def init_channel(self, context, poll, link):

        client = context.socket(zmq.REQ)
        client.connect(link)
        poll.register(client, zmq.POLLIN)

        return client


    def send(self, send_str, isjson = False):
        try:
            self.client.send(send_str)
            print(">>>1")
            ret = self.recv()
            print(ret)
            if isjson:
                return json.loads(ret)
            else:
                return ret
        except Exception as e:
            print(e)
            return None

    def close(self):
        self.client.disconnect(self.con_str)
        pass


class ZmqServUtil():
    def __init__(self, con_str, dealer_func):
        self.context = zmq.Context()
        self.poll = zmq.Poller()

        self.con_str = con_str

        self.t_obj = threading.Thread(target=self.run, args=(dealer_func,))
        self.t_obj.daemon = True
        self.t_obj.start()

    def init_channel(self, context, poll, link):
        serv = context.socket(zmq.REP)
        serv.bind(link)
        poll.register(serv, zmq.POLLIN)
        return serv

    def stop(self):
        self.is_stop = True
        self.context = None
        self.poll = None
        self.t_obj.join()

    def run(self, dealer_func):
        reply = "ok"
        serv = self.init_channel(self.context, self.poll, self.con_str)
        self.is_stop = False
        while 1:
            if self.is_stop:
                break
            socks = dict(self.poll.poll(2))
            if socks.get(serv) == zmq.POLLIN:
                req_str = serv.recv()
                if None != dealer_func:
                    reply = dealer_func(req_str)
                serv.send(reply)
        print("close ZmqServ")

if __name__ == '__main__':
    import time,json
    

    import time
    f = lambda x: "dealer ok"
    s = ZmqServUtil("tcp://*:6666",f)
    while 1:
        time.sleep(1)
        
        
