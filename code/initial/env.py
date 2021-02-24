import os, signal, sys, time, argparse, math, collections
import matplotlib.pyplot as plt
from acceptor import Acceptor
from leader import Leader
from message import RequestMessage
from process import Process
from replica import Replica
from clients import Clients
from utils import *

class Env:
  def __init__(self, replicas, leaders, acceptors, configs, clients):
    self.NACCEPTORS = acceptors
    self.NREPLICAS = replicas
    self.NLEADERS = leaders
    self.NCLIENTS = clients
    self.NCONFIGS = configs
    self.NREQUESTS = 10
    self.procs = {}
    self.acceptedNumber = 0
    self.d = {}
    self.od = {}
    self.time = {}

  def sendMessage(self, dst, msg):
    if dst in self.procs:
      self.procs[dst].deliver(msg)

  def addProc(self, proc):
    self.procs[proc.id] = proc
    proc.start()

  def removeProc(self, pid):
    del self.procs[pid]

  def _initializeCluster(self, c, initialconfig):
    for i in range(self.NREPLICAS):
      pid = "replica %d" % i
      Replica(self, pid, initialconfig)
      initialconfig.replicas.append(pid)
    for i in range(self.NACCEPTORS):
      pid = "acceptor %d.%d" % (c,i)
      Acceptor(self, pid)
      initialconfig.acceptors.append(pid)
    for i in range(self.NLEADERS):
      pid = "leader %d.%d" % (c,i)
      Leader(self, pid, initialconfig)
      initialconfig.leaders.append(pid)

    for c in range(1, self.NCONFIGS):
      # Create new configuration
      config = Config(initialconfig.replicas, [], [])
      for i in range(self.NACCEPTORS):
        pid = "acceptor %d.%d" % (c,i)
        Acceptor(self, pid)
        config.acceptors.append(pid)
      for i in range(self.NLEADERS):
        pid = "leader %d.%d" % (c,i)
        Leader(self, pid, config)
        config.leaders.append(pid)
      # Send reconfiguration request
      for r in config.replicas:
        pid = "master %d.%d" % (c,i)
        cmd = ReconfigCommand(pid,0,str(config))
        self.sendMessage(r, RequestMessage(pid, cmd))
        time.sleep(1)
      for i in range(WINDOW-1):
        pid = "master %d.%d" % (c,i)
        for r in config.replicas:
          cmd = Command(pid,0,"operation noop")
          self.sendMessage(r, RequestMessage(pid, cmd))
          time.sleep(1)

    return config

  def _sendConcurrentRequests(self, id, c, replicas):
    num = (self.NREQUESTS*c)+1
    key = self.NREQUESTS*c
    #print key
    self.time[key] = True
    for i in range(1, num):
      pid = "client %d.%d" % (c,i)
      for r in replicas:
        cmd = Command(pid,id,"operation %d.%d" % (c,i))
        self.sendMessage(r,RequestMessage(pid,cmd))
        time.sleep(1)
    self.time[key] = False

  def run(self):
    initialconfig = Config([], [], [])
    c = 0

    print "Welcome to PaxosMMC evaluation.\nPlease wait to paxos cluster initialize...\n"

    cfg = self. _initializeCluster(c, initialconfig)
    time.sleep((self.NCONFIGS)*len(cfg.replicas)*len(cfg.leaders))
    
    raw_input("\nPress Enter to start evaluation...\n")

    start_time = time.time()
    for c in range(1, self.NCLIENTS+1):
      self.d[self.NREQUESTS * c] = 0
      self.time[self.NREQUESTS * c] = True
      self._sendConcurrentRequests(self.NREQUESTS * c, c, cfg.replicas)
      #Clients(self, c, self.NREQUESTS, cfg.replicas)

    end_time = time.time()
    total = end_time - start_time
    print "Elapsed time: ", total

    #print self.time

    t = all(value == False for value in self.time.values())

    if t == True:
      self._drawGraph()

  def _drawGraph(self):
    a = {k: v / (self.NREPLICAS*self.NLEADERS) for k, v in self.d.iteritems()}
    self.od = collections.OrderedDict(sorted(a.iteritems()))
    x = self.od.keys()
    y = self.od.values()
    yerr = 0.1 + 0.2*math.sqrt(len(y))
    fig, ax = plt.subplots()
    ax.errorbar(x, y, yerr=yerr, marker='s', ms=3, mew=4)
    plt.show()

    if (args.nopdf is False):
      fig.savefig("figure.pdf", bbox_inches='tight')

  def terminate_handler(self, signal, frame):
    #raw_input("Press Enter to shutdown paxos cluster ...")
    self._graceexit()

  def _graceexit(self, exitcode=0):
    sys.stdout.flush()
    sys.stderr.flush()
    os._exit(exitcode)

def parse_args():
    parser = argparse.ArgumentParser(prog="test_paxosmmc", description="the test automation script for paxosmmc")
    parser.add_argument("--replicas","-r", type=int, default=2, help="The number of replicas (default {})".format(2))
    parser.add_argument("--leaders", "-l", type=int, default=2, help="The number of leaders (default {})".format(2))
    parser.add_argument("--acceptors","-a", type=int, default=3, help="The number of acceptors (default {})".format(3))
    parser.add_argument("--configs","-cf", type=int, default=2, help="The number of configs (default {})".format(2))
    parser.add_argument("--clients","-c", type=int, default=1, help="The upper threshold of concurrent clients (default {})".format(10))
    parser.add_argument("--nopdf", type=bool,default=False,const=True, nargs="?" , help="saving of pdf (default {})".format(False))
    return parser.parse_args()

def main(args):
  e = Env(args.replicas, args.leaders, args.acceptors, args.configs, args.clients)
  e.run()
  signal.signal(signal.SIGINT, e.terminate_handler)
  signal.signal(signal.SIGTERM, e.terminate_handler)
  signal.pause()

if __name__=='__main__':
  args = parse_args() 
  main(args)
