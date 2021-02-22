from process import Process
from message import ProposeMessage,DecisionMessage,RequestMessage
from utils import *
import time

class Clients(Process):
  def __init__(self, env, id, nRequests, replicas):
    Process.__init__(self, env, id)
    self.nRequests = nRequests
    self.replicas = replicas
    self.env.addProc(self)

  def body(self):
    for i in range(self.nRequests):
      pid = "client %d.%d" % (self.id,i)
      for r in self.replicas:
        cmd = Command(pid,0,"operation %d.%d" % (self.id,i))
        self.sendMessage(r,RequestMessage(pid,cmd))
        time.sleep(1)
