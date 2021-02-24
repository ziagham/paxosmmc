from process import Process
from message import ProposeMessage,DecisionMessage,RequestMessage
from utils import *
import time

class Clients(Process):
  def __init__(self, env, c, nRequests, replicas):
    self.id = nRequests * c
    self.nRequests = nRequests
    self.replicas = replicas
    self.c = c
    Process.__init__(self, env, self.id)
    self.env.addProc(self)

  def body(self):
    num = (self.nRequests*self.c)+1
    id = self.nRequests*self.c
    for i in range(1, num):
      pid = "client %d.%d" % (self.c,i)
      for r in self.replicas:
        cmd = Command(pid,id,"operation %d.%d" % (self.c,i))
        self.sendMessage(r,RequestMessage(pid,cmd))
        time.sleep(1)


    # for i in range(self.nRequests):
    #   pid = "client %d.%d" % (self.id,i)
    #   for r in self.replicas:
    #     cmd = Command(pid,0,"operation %d.%d" % (self.id,i))
    #     self.sendMessage(r,RequestMessage(pid,cmd))
    #     time.sleep(1)
