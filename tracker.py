import spade, time, random, ast

def getAddress(name):
	host = '127.0.0.1'
	return name +'@'+ host

have, want = {}, {}
class TrackerAgent(spade.Agent.Agent):
	class TrackerBehaviour(spade.Behaviour.EventBehaviour):
		def _process(self):
			msg = self._receive(True)
			mdict = ast.literal_eval(msg.getContent())

			def appendListToTable(di, li):
				name = mdict['name']
				for i in li:
					if i in di:
						if not name in di[i]: di[i] += [name]
					else: di[i] = [name]

			# update have and want dicts
			appendListToTable(have, mdict['have'])
			appendListToTable(want, mdict['want'])

			# reply sender with newest info
			rep = msg.createReply()
			rep.setPerformative('inform')
			rep.setContent({'type': 'tracker', 'want': want, 'have': have})
			self.myAgent.send(rep)

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