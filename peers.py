import spade, time, random, math, hashlib, ast

def getAddress(name):
	host = '127.0.0.1'
	return name +'@'+ host

def segmentFile(file):
	parts = 100
	step = int(math.ceil(float(len(file)) / parts))
	parts = [file[i*step:i*step+step] for i in range(parts)]

	segments = dict()
	cry = hashlib.sha1()
	for part in parts:
		cry.update(part)
		segments[cry.hexdigest()] = part

	return segments

class TorrentAgent(spade.Agent.Agent):
	def __init__(self, name, want, have):
		self._name, self._want, self._have, self._others = name, want, have, {}

		super(TorrentAgent, self).__init__(getAddress(self._name), "secret")
		self.wui.start()
		self.start()

	def _setup(self):
		bhv = self.TorrentBehaviour()
		self.addBehaviour(bhv, None)

		# register message receiver
		template = spade.Behaviour.ACLTemplate()
		template.addReceiver(spade.AID.aid(getAddress(self._name), ['xmpp://'+ getAddress(self._name)]))
		self.addBehaviour(self.ReceiveBehaviour(), spade.Behaviour.MessageTemplate(template))

	class ReceiveBehaviour(spade.Behaviour.EventBehaviour):
		def _process(self):
			msg = self._receive(True)
			if msg.getContent().startswith('{'):
				content = ast.literal_eval(msg.getContent())
				self.myAgent._others = content

	class TorrentBehaviour(spade.Behaviour.OneShotBehaviour):
		def _process(self):
			content = {'name': self.myAgent._name, 'want': self.myAgent._want, 'have': self.myAgent._have.keys()}
			self.askTracker(content)

		def askTracker(self, content):
			msg = spade.ACLMessage.ACLMessage('request')
			msg.addReceiver(spade.AID.aid(getAddress('tracker'), ['xmpp://'+ getAddress('tracker')]))
			msg.setContent(content)
			self.myAgent.send(msg)

# execution
if __name__ == "__main__":
	
	file = ','.join([str(x) for x in range(1000)])
	segments = segmentFile(file)

	peer_count = 5
	peers = []
	for i in range(peer_count):
		if i == 0:
			want = []; have = segments
		else:
			want = segments.keys(); have = {}

		peers.append(TorrentAgent('peer' + str(i), want, have))

	alive = True
	while alive:
		try: time.sleep(1) 
		except KeyboardInterrupt: alive=False
	
	for i in range(peer_count):
		peers[i].stop()