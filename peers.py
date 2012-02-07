import spade, time, random
host = '127.0.0.1'

class TorrentAgent(spade.Agent.Agent):
	def __init__(self, name):
		self._name = name
		super(TorrentAgent, self).__init__(self._name +"@"+ host, "secret")
		self.wui.start()
		self.start()

	class TorrentBehaviour(spade.Behaviour.OneShotBehaviour):
		def _process(self):
			self.askTracker(self.myAgent._name)

		def askTracker(self, content):
			msg = spade.ACLMessage.ACLMessage('request')
			msg.addReceiver(spade.AID.aid("tracker@"+host,["xmpp://tracker@"+host]))
			msg.setContent(content)
			self.myAgent.send(msg)

	def _setup(self):
		bhv = self.TorrentBehaviour()
		self.addBehaviour(bhv, None)

# execution
if __name__ == "__main__":
	peer_count = 5
	peers = [];
	for i in range(peer_count):
		peers.append(TorrentAgent('peer' + str(i)))

	alive = True
	while alive:
		try: time.sleep(1) 
		except KeyboardInterrupt: alive=False
	
	for i in range(peer_count):
		peers[i].stop()