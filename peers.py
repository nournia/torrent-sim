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

def addToDict(dic, key, value):
	if not key in dic:
		dic[key] = [value]
	elif not value in dic[key]:
		dic[key] += [value]

def getKeys(dic, value):
	keys = []
	for key, vals in dic.items():
		if value in vals:
			keys.append(key)
	return keys

def listDiff(list1, list2):
	return list(set(list1) ^ set(list2))

class TorrentAgent(spade.Agent.Agent):
	def __init__(self, name, want, have, bwUp, bwDown):
		self._name, self._bwUp, self._bwDown = name, bwUp, bwDown
		self._segments = have # sha1 indexed strings
		self._have = have.keys() # segment list
		self._want = want # segment list
		self._interest = {} # I sent interest message for these peers because of segments list
		self._unchoke = [] # These peers unchoked me

		# have: sha1 indexed lists of peers
		# interest: which peer wants which segments
		# unchoked: I unchocked these peers
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

			if msg.getContent().startswith('{'):
				content = ast.literal_eval(msg.getContent())
				agent = self.myAgent
				sender = getName(msg)

				# print sender, 'to', agent._name, ':', content
				if content['type'] == 'tracker':
					agent._others['have'] = content['have']

				elif content['type'] == 'interest':
					addToDict(agent._others['interest'], sender, content['piece'])

				elif content['type'] == 'not-interest':
					if sender in agent._others['interest']:
						agent._others['interest'][sender].remove(content['piece'])
						if not agent._others['interest'][sender]:
							agent._others['interest'].pop(sender)

				elif content['type'] == 'choke':
					agent._unchoke.remove(sender)

				elif content['type'] == 'unchoke':
					agent._unchoke.append(sender)

				elif content['type'] == 'request':
					if sender in agent._others['unchoked']:
						agent.replyMsg(msg, {'type': 'piece', 'piece': content['piece'], 'segment': agent._segments[content['piece']], 'bw': agent._bwUp}, 'agree')

				elif content['type'] == 'piece':
					agent._segments[content['piece']] = content['segment']
					if content['piece'] not in agent._have:
						agent._have.append(content['piece'])
					if content['piece'] in agent._want:
						agent._want.remove(content['piece'])

					peers = getKeys(agent._interest, content['piece'])
					for peer in peers:
						agent.sendMsg(peer, {'type': 'not-interest', 'piece': content['piece']})
						agent._interest[peer].remove(content['piece'])

					# print sender, 'to', agent._name
					print agent._name, 'pieces:', len(agent._have), len(set(agent._have)), 'unchoke:', len(agent._unchoke)


	class TorrentBehaviour(spade.Behaviour.OneShotBehaviour):
		def _process(self):
			agent = self.myAgent

			agent.sendMsg('tracker', {'have': agent._have})
			while 1:
				try:
					# ask tracker
					if not random.randint(0, 5):
						agent.sendMsg('tracker', {'have': agent._have})

					# send interset message
					if agent._want:
						piece = random.choice(agent._want)
						sent = getKeys(agent._interest, piece)
						if not sent and piece in agent._others['have']:
							peer = random.choice(agent._others['have'][piece])
							agent.sendMsg(peer, {'type': 'interest', 'piece': piece})
							addToDict(agent._interest, peer, piece)

					# send uchocke message
					if len(agent._others['interest']) > 0:
						peer = random.choice(list(set(agent._others['interest'].keys()) ^ set(agent._others['unchoked'])))
						agent.sendMsg(peer, {'type': 'unchoke', 'bw': agent._bwUp})
						agent._others['unchoked'].append(peer)

					# send request message
					for peer in agent._unchoke:
						pieces = listDiff(getKeys(agent._others['have'], peer), agent._have)
						if pieces:
							agent.sendMsg(peer, {'type': 'request', 'piece': random.choice(pieces), 'bw': agent._bwDown}, 'request')

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