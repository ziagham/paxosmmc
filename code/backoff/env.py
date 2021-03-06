import os, signal, sys, time, argparse, math, collections
import matplotlib.pyplot as plt
from acceptor import Acceptor
from leader import Leader
from message import RequestMessage
from process import Process
from replica import Replica
#from clients import Clients
from utils import *
from datetime import datetime

class Env:
    """
    This is the main code in which all processes are created and run. This
    code also simulates a set of clients submitting requests.
    """
    def __init__(self, replicas, leaders, acceptors, configs, clients, nopdf):
        self.NACCEPTORS = acceptors
        self.NREPLICAS = replicas
        self.NLEADERS = leaders
        self.NCONFIGS = configs
        self.NREQUESTS = clients
        self.nopdf = nopdf
        self.procs = {}
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

    def _reConfig(self, c, initialconfig): 
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
            cmd = ReconfigCommand(pid,-1,str(config))
            self.sendMessage(r, RequestMessage(pid, cmd))
            time.sleep(1)
        for i in range(WINDOW-1):
            pid = "master %d.%d" % (c,i)
            for r in config.replicas:
                cmd = Command(pid,-1,"operation noop")
                self.sendMessage(r, RequestMessage(pid, cmd))
                time.sleep(1)

        return config

    def _sendConcurrentRequests(self, to, config):
        c = to
        self.time[c] = True
        for i in range(1, c+1):
            pid = "client %d.%d" % (c,i)
            for r in config.replicas:
                cmd = Command(pid,c,"operation %d.%d" % (c,i))
                self.sendMessage(r,RequestMessage(pid,cmd))
                time.sleep(1)
        self.time[c] = False


    def run(self):
        initialconfig = Config([], [], [])
        c = 0

        print "Welcome to PaxosMMC evaluation.\nPlease wait to paxos cluster initialize...\n"

        self. _initializeCluster(c, initialconfig)
        time.sleep((self.NCONFIGS)*len(initialconfig.replicas)*len(initialconfig.leaders))
        
        raw_input("\nPress Enter to start evaluation...\n")

        start_time = time.time()
        for c in range(0, self.NREQUESTS+1, 1):
            self.d[c] = 0
            self.time[c] = True
            #cfg = self._reConfig(c, initialconfig)
            self._sendConcurrentRequests(c, initialconfig)
            #Clients(self, c, cfg.replicas)

        end_time = time.time()
        total = end_time - start_time
        print "Elapsed time: ", total

        #t = all(value == False for value in self.time.values())
        #if t == True:
        self._drawGraph()

    def _drawGraph(self):
        a = {k: v / (self.NREPLICAS) for k, v in self.d.iteritems()}
        self.od = collections.OrderedDict(sorted(a.iteritems()))
        x = self.od.keys()
        y = self.od.values()
        yerr = 0.1 + 0.2*math.sqrt(len(y))
        fig, ax = plt.subplots()
        ax.errorbar(x, y, yerr=yerr, label='Accept throughput',color="red",marker="o")
        ax.legend(title='Accept throughput')
        
        plt.title('PaxosMMC Accept throughput')
        plt.legend()
        plt.xlabel('Clients (Request/s)')
        plt.ylabel('Accept throughput (Request/s)')
        plt.xlim(0, self.NREQUESTS)
        plt.ylim(0, self.NREQUESTS)
        plt.grid(b=True, which='major', color='#ececec', linestyle='-')

        plt.show()

        if (self.nopdf == False):
            fig.savefig("figure_"+str(datetime.now())+".pdf", bbox_inches='tight')


        # # Create replicas
        # for i in range(NREPLICAS):
        #     pid = "replica %d" % i
        #     Replica(self, pid, initialconfig)
        #     initialconfig.replicas.append(pid)
        # # Create acceptors (initial configuration)
        # for i in range(NACCEPTORS):
        #     pid = "acceptor %d.%d" % (c,i)
        #     Acceptor(self, pid)
        #     initialconfig.acceptors.append(pid)
        # # Create leaders (initial configuration)
        # for i in range(NLEADERS):
        #     pid = "leader %d.%d" % (c,i)
        #     Leader(self, pid, initialconfig)
        #     initialconfig.leaders.append(pid)
        # # Send client requests to replicas
        # for i in range(NREQUESTS):
        #     pid = "client %d.%d" % (c,i)
        #     for r in initialconfig.replicas:
        #         cmd = Command(pid,0,"operation %d.%d" % (c,i))
        #         self.sendMessage(r, RequestMessage(pid,cmd))
        #         time.sleep(1)

        # # Create new configurations. The configuration contains the
        # # leaders and the acceptors (but not the replicas).
        # for c in range(1, NCONFIGS):
        #     config = Config(initialconfig.replicas, [], [])
        #     # Create acceptors in the new configuration
        #     for i in range(NACCEPTORS):
        #         pid = "acceptor %d.%d" % (c,i)
        #         Acceptor(self, pid)
        #         config.acceptors.append(pid)
        #     # Create leaders in the new configuration
        #     for i in range(NLEADERS):
        #         pid = "leader %d.%d" % (c,i)
        #         Leader(self, pid, config)
        #         config.leaders.append(pid)
        #     # Send reconfiguration request
        #     for r in config.replicas:
        #         pid = "master %d.%d" % (c,i)
        #         cmd = ReconfigCommand(pid,0,str(config))
        #         self.sendMessage(r, RequestMessage(pid, cmd))
        #         time.sleep(1)
        #     # Send WINDOW noops to speed up reconfiguration
        #     for i in range(WINDOW-1):
        #         pid = "master %d.%d" % (c,i)
        #         for r in config.replicas:
        #             cmd = Command(pid,0,"operation noop")
        #             self.sendMessage(r, RequestMessage(pid, cmd))
        #             time.sleep(1)
        #     # Send client requests to replicas
        #     for i in range(NREQUESTS):
        #         pid = "client %d.%d" % (c,i)
        #         for r in config.replicas:
        #             cmd = Command(pid,0,"operation %d.%d"%(c,i))
        #             self.sendMessage(r, RequestMessage(pid, cmd))
        #             time.sleep(1)

    def terminate_handler(self, signal, frame):
        a = {k: v / (self.NREPLICAS) for k, v in self.d.iteritems()}
        print a
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
    parser.add_argument("--clients","-c", type=int, default=10, help="The upper threshold of concurrent clients (default {})".format(10))
    parser.add_argument("--nopdf", type=bool,default=False,const=True, nargs="?" , help="Saving of pdf (default {})".format(False))
    return parser.parse_args()

def main(args):
    e = Env(args.replicas, args.leaders, args.acceptors, args.configs, args.clients, args.nopdf)
    e.run()
    e._graceexit(0)

if __name__=='__main__':
    args = parse_args() 
    main(args)
