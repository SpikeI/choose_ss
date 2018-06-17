#/usr/bin/python
import subprocess
import threading
from icmp_ping_tool import Pinger
import Queue
import json


class Choose(object):

    def __init__(self):
        self.server_file = ''
        self.server_list = []
        self.server_queue = Queue.Queue()
        self.key = ''
        self.method = ''
        self.server_port = 0
        self.listen_port = 0
        self.listen_addr = '127.0.0.1'
        self.server_num = 0
        self.THREAD_NUM = 5
        self.best_server = ''
        self.best_speed = 999999
        self.done = 0
        self.server_count = 0
        self.lock = threading.Lock()


    def test_speed(self):
        '''
        Test the Speed in Queue
        if the server is faster
        then change the self. Best_server  and self.Best_speed
        '''
        while not self.server_queue.empty():
            #print '[=] Prepare to get a server'
            server_addr = self.server_queue.get()
            pinger = Pinger(server_addr)
            time = pinger.ping()
            self.lock.acquire()
            if time < self.best_speed:
                print '[+] Find Better server '+server_addr+' with delay '+ str(time) +' !'
                self.best_server = server_addr
                self.best_speed = time
            self.lock.release()
            self.server_queue.task_done()
            # break
        pass

    def read_server_file(self):
        with open('server.config','r') as f:
            content = f.read()
        content = json.loads(content)
        self.server_list = content["server_addr"]
        self.server_port = content["server_port"]
        self.listen_addr = content["listen_addr"]
        self.listen_port = content["listen_port"]
        self.key = content["key"]
        self.method = content["method"]
        self.server_count = len(self.server_list)

        print '[+] We Got ' + str(self.server_count) + ' server in the list!'
        for i in self.server_list:
            self.server_queue.put(i)
            # print i

    def attach_ss(self, addr):
        #server_addr = self.server_queue.get();
        cmd = 'sslocal -s {} -p {} -k {} -m {} -b {} -l {} &'.format(addr, self.server_port, self.key, self.method, self.listen_addr, self.listen_port)
        print cmd
        res = subprocess.check_output(cmd, shell=True)
        print res

    def choose_speed(self):
        for i in range(self.THREAD_NUM):
            t = threading.Thread(target = self.test_speed)
            t.start()
        self.server_queue.join()
        print '[+] The best server is '+self.best_server+' with speed ' + str(self.best_speed) + ' !'

    def main(self):
        addr = ''
        # read_file get list Queue && server length
        self.read_server_file()
        # test each server' react time
        self.choose_speed()
        # choose the fastest one and attach it
        self.attach_ss(self.best_server)


c = Choose()
c.main()
