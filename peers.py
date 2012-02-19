import spade, time, random, math, hashlib, ast

def getAddress(name):
	host = '127.0.0.1'
	return name +'@'+ host

def getName(msg):
	return msg.getSender().getName().split('@')[0]

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
	def __init__(self, name, want, have, bwUp, bwDown):
		self._name, self._bwUp, self._bwDown = name, bwUp, bwDown
		self._segments = have # sha1 indexed strings
		self._have = have.keys() # segment list
		self._want = want # segment list
		self._interest = [] # segment list

		# have: sha1 indexed lists of peers
		# interest: which peer wants which segments
		# unchoked: list of unchoked peers
		self._others = {'have': {}, 'interest': {}, 'unchoked': []}

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

	def getPeerPieces(self, peer):
		pieces = []
		for piece, peers in self._others['have'].items():
			if peer in peers:
				pieces.append(piece)
		return pieces

	def sendMsg(self, receiver, content, kind = 'inform'):
		msg = spade.ACLMessage.ACLMessage(kind)
		msg.addReceiver(spade.AID.aid(getAddress(receiver), ['xmpp://'+ getAddress(receiver)]))
		msg.setContent(content)
		self.send(msg)

	def replyMsg(self, msg, content, kind = 'inform'):
		rep = msg.createReply()
		rep.setPerformative(kind)
		rep.setContent(content)
		self.send(rep)


	class ReceiveBehaviour(spade.Behaviour.EventBehaviour):
		def _process(self):
			msg = self._receive(True)

			def addToDict(dic, key, value):
				if not key in dic:
					dic[key] = [value]
				elif not value in dic[key]:
					dic[key] += [value]

			if msg.getContent().startswith('{'):
				content = ast.literal_eval(msg.getContent())
				agent = self.myAgent
				sender = getName(msg)

				# print sender, 'to', agent._name, ':', content
				if content['type'] == 'tracker':
					agent._others['have'] = content['have']

				elif content['type'] == 'interest':
					addToDict(agent._others['interest'], sender, content['segment'])

				elif content['type'] == 'unchoke':
					pieces = agent.getPeerPieces(sender)
					if pieces:
						agent.replyMsg(msg, {'type': 'request', 'piece': random.choice(pieces), 'bw': agent._bwDown}, 'request')

				elif content['type'] == 'request':
					if sender in agent._others['unchoked']:
						agent.replyMsg(msg, {'type': 'piece', 'piece': content['piece'], 'segment': agent._segments[content['piece']], 'bw': agent._bwUp}, 'agree')

				elif content['type'] == 'piece':
					agent._segments[content['piece']] = content['segment']
					agent._have.append(content['piece'])


	class TorrentBehaviour(spade.Behaviour.OneShotBehaviour):
		def _process(self):
			agent = self.myAgent

			# ask tracker
			agent.sendMsg('tracker', {'have': agent._have})

			while 1:
				try:
					# send interset message
					if agent._want:
						segment = random.choice(agent._want)
						if segment in agent._others['have']:
							peer = random.choice(agent._others['have'][segment])
							agent.sendMsg(peer, {'type': 'interest', 'segment': segment})
							agent._interest.append(segment)
							agent._want.remove(segment)

					# send uchocke message
					if len(agent._others['interest']) > 0:
						peer = random.choice(list(set(agent._others['interest'].keys()) ^ set(agent._others['unchoked'])))
						agent.sendMsg(peer, {'type': 'unchoke', 'bw': agent._bwUp})
						agent._others['unchoked'].append(peer)

				except: pass
				time.sleep(1)

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

		bwUp, bwDown = 500, 1000
		peers.append(TorrentAgent('peer' + str(i), want, have, bwUp, bwDown))
		# peers[i].setDebugToScreen()

	alive = True
	while alive:
		try: time.sleep(1)
		except KeyboardInterrupt: alive=False
	
	for i in range(peer_count):
		peers[i].stop()