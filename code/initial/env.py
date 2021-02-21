import os, signal, sys, time, argparse, math
import matplotlib.pyplot as plt
from acceptor import Acceptor
from leader import Leader
from message import RequestMessage
from process import Process
from replica import Replica
from utils import *

# NACCEPTORS = 3
# NREPLICAS = 2
# NLEADERS = 2
# NREQUESTS = 10
# NCONFIGS = 2

class Env:
  def __init__(self, replicas, leaders, acceptors, configs, requests):
    self.NACCEPTORS = acceptors
    self.NREPLICAS = replicas
    self.NLEADERS = leaders
    self.NREQUESTS = requests
    self.NCONFIGS = configs
    self.procs = {}
    self.acceptedNumber = 0

  def sendMessage(self, dst, msg):
    if dst in self.procs:
      self.procs[dst].deliver(msg)

  def addProc(self, proc):
    self.procs[proc.id] = proc
    proc.start()

  def removeProc(self, pid):
    del self.procs[pid]

  def addAcceptedNumber(self):
    self.acceptedNumber += 1
    #print "Accepted Number: ", self.acceptedNumber

  def run(self):
    initialconfig = Config([], [], [])
    c = 0

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

    start_time = time.time()
    for i in range(self.NREQUESTS):
      pid = "client %d.%d" % (c,i)
      for r in initialconfig.replicas:
        cmd = Command(pid,0,"operation %d.%d" % (c,i))
        self.sendMessage(r,RequestMessage(pid,cmd))
        time.sleep(1)

    end_time = time.time()
    total = end_time - start_time
    print "Total time to become stable: ", total
    print "AcceptedNumber: ", self.acceptedNumber / (self.NLEADERS)


    # a_dictionary = {"100": 100, "200": 200, "300": 300}
    # x = a_dictionary.keys()
    # y = a_dictionary.values()

    # yerr = 0.1 + 0.2*math.sqrt(len(y))

    # fig, ax = plt.subplots()

    # ax.errorbar(x, y,
    #         yerr=yerr,
    #         marker='s', ms=3, mew=4)

    # plt.show()

    # plt.plot(keys, values)

    # for c in range(1, self.NCONFIGS):
    #   # Create new configuration
    #   config = Config(initialconfig.replicas, [], [])
    #   for i in range(self.NACCEPTORS):
    #     pid = "acceptor %d.%d" % (c,i)
    #     Acceptor(self, pid)
    #     config.acceptors.append(pid)
    #   for i in range(self.NLEADERS):
    #     pid = "leader %d.%d" % (c,i)
    #     Leader(self, pid, config)
    #     config.leaders.append(pid)
    #   # Send reconfiguration request
    #   for r in config.replicas:
    #     pid = "master %d.%d" % (c,i)
    #     cmd = ReconfigCommand(pid,0,str(config))
    #     self.sendMessage(r, RequestMessage(pid, cmd))
    #     time.sleep(1)
    #   for i in range(WINDOW-1):
    #     pid = "master %d.%d" % (c,i)
    #     for r in config.replicas:
    #       cmd = Command(pid,0,"operation noop")
    #       self.sendMessage(r, RequestMessage(pid, cmd))
    #       time.sleep(1)

      

    #   for i in range(self.NREQUESTS):
    #     pid = "client %d.%d" % (c,i)
    #     for r in config.replicas:
    #       cmd = Command(pid,0,"operation %d.%d"%(c,i))
    #       self.sendMessage(r, RequestMessage(pid, cmd))
    #       time.sleep(1)



  def terminate_handler(self, signal, frame):
    #print "accepted: " ,self.acceptedNumber
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
  e = Env(args.replicas, args.leaders, args.acceptors, args.configs, args.clients)
  e.run()
  signal.signal(signal.SIGINT, e.terminate_handler)
  signal.signal(signal.SIGTERM, e.terminate_handler)
  signal.pause()

if __name__=='__main__':
  args = parse_args() 
  main(args)
