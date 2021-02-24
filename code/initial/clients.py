from process import Process
from message import ProposeMessage,DecisionMessage,RequestMessage
from utils import *
import time

class Clients(Process):
  def __init__(self, env, to, replicas):
    self.replicas = replicas
    self.to = to
    Process.__init__(self, env, to)
    self.env.addProc(self)

  def body(self):
    c = self.to
    for i in range(1, c+1):
      pid = "client %d.%d" % (c,i)
      for r in self.replicas:
        cmd = Command(pid,c,"operation %d.%d" % (c,i))
        self.sendMessage(r,RequestMessage(pid,cmd))
        time.sleep(1)