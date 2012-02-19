import spade, time, random, ast

def getAddress(name):
	host = '127.0.0.1'
	return name +'@'+ host

def getName(msg):
	return msg.getSender().getName().split('@')[0]

have = {}
class TrackerAgent(spade.Agent.Agent):
	class TrackerBehaviour(spade.Behaviour.EventBehaviour):
		def _process(self):
			msg = self._receive(True)

			if msg.getContent().startswith('{'):
				content = ast.literal_eval(msg.getContent())
				sender = getName(msg)
	
				def appendListToTable(di, li):
					for i in li:
						if i in di:
							if not sender in di[i]: di[i].append(sender)
						else: di[i] = [sender]

				appendListToTable(have, content['have'])

				# reply sender with newest info
				rep = msg.createReply()
				rep.setPerformative('inform')
				rep.setContent({'type': 'tracker', 'have': have})
				self.myAgent.send(rep)

				# stats
				clients = {}
				for piece, peers in have.items():
					for peer in peers:
						if peer in clients:
							clients[peer] += 1
						else:
							clients[peer] = 1

				for name, pieces in clients.items():
					print '{}: {}%'.format(name, pieces),
				print

	def _setup(self):
		template = spade.Behaviour.ACLTemplate()
		template.addReceiver(spade.AID.aid(getAddress('tracker'), ['xmpp://'+ getAddress('tracker')]))
		self.addBehaviour(self.TrackerBehaviour(), spade.Behaviour.MessageTemplate(template))

# execution
if __name__ == "__main__":

	tracker = TrackerAgent(getAddress('tracker'), "secret")
	tracker.wui.start()
	tracker.start()

	alive = True
	while alive:
		try: time.sleep(1) 
		except KeyboardInterrupt: alive=False

	tracker.stop()