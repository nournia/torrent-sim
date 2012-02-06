import spade, time, random

class TorrentAgent(spade.Agent.Agent):
	def __init__(self, name):
		self._name = name
		super(TorrentAgent, self).__init__("{}@127.0.0.1".format(self._name), "secret")
		self.wui.start()
		self.start()

	class TorrentBehaviour(spade.Behaviour.OneShotBehaviour):
		def _process(self):
			print self.myAgent._name

	def _setup(self):
		bhv = self.TorrentBehaviour()
		self.addBehaviour(bhv, None)

# execution
if __name__ == "__main__":
	peers = [];
	for i in range(10):
		peers.append(TorrentAgent('peer' + str(i)))

	alive = True
	while alive:
		try: time.sleep(1) 
		except KeyboardInterrupt: alive=False
	
	for i in range(10):
		peers[i].stop()