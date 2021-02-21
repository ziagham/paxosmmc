import os, signal, sys, time
import argparse
import subprocess
from env import *

# class ClusterRatio:
#     def __init__(self, acceptors, replicas, leaders, requests, configs):
#         self.acceptors = acceptors
#         self.replicas = replicas
#         self.leaders = leaders
#         self.requests = requests
#         self.configs = configs

class Test:
    def __init__(self, replicas, leaders, acceptors, configs, clients):
        self.replicas = leaders
        self.leaders = leaders
        self.acceptors = acceptors
        self.configs = configs
        self.clients = clients

    # def _calculateRatio(self):
    #     acceptors = self.size
    #     replicas = self.size-1
    #     leaders = self.size-1
    #     configs = self.size-1
    #     return ClusterRatio(acceptors,replicas,leaders,self.requests,configs)

    def runTest(self):
        # ratio = self._calculateRatio()
        e = Env(self.replicas, self.leaders, self.acceptors, self.configs, self.clients)
        e.run()
        signal.signal(signal.SIGINT, e.terminate_handler)
        signal.signal(signal.SIGTERM, e.terminate_handler)
        signal.pause()

    def terminate_handler(self, signal, frame):
        self._graceexit()

    def _graceexit(self, exitcode=0):
        sys.stdout.flush()
        sys.stderr.flush()
        os._exit(exitcode)

def parse_args():
    parser = argparse.ArgumentParser(prog="test_paxosmmc", description="the test automation script for paxosmmc")
    parser.add_argument("--replicas", type=int, default=2, help="The number of replicas (default {})".format(2))
    parser.add_argument("--leaders", type=int, default=2, help="The number of leaders (default {})".format(2))
    parser.add_argument("--acceptors", type=int, default=3, help="The number of acceptors (default {})".format(3))
    parser.add_argument("--configs", type=int, default=2, help="The number of configs (default {})".format(2))
    parser.add_argument("--clients", type=int, default=10, help="The size of clients (default {})".format(10))
    return parser.parse_args()
    
def main(args):
  t = Test(args.replicas, args.leaders, args.acceptors, args.configs, args.clients)
  t.runTest()
  signal.signal(signal.SIGINT, t.terminate_handler)
  signal.signal(signal.SIGTERM, t.terminate_handler)
  signal.pause()

if __name__=='__main__':
    args = parse_args()
    main(args)
