import spade, time, random, ast
host = '127.0.0.1'

have, want = {}, {}
class TrackerAgent(spade.Agent.Agent):
	class TrackerBehaviour(spade.Behaviour.EventBehaviour):
		def _process(self):
			msg = self._receive(True)
			mdict = ast.literal_eval(msg.getContent())

			def appendListToTable(di, li):
				name = mdict['name']
				for i in li:
					if di.has_key(i): di[i] += [name]
					else: di[i] = [name]

			# update have and want dicts
			appendListToTable(have, mdict['have'])
			appendListToTable(want, mdict['want'])

			# reply sender with newest info
			rep = msg.createReply()
			rep.setPerformative('inform')
			rep.setContent({'want': want, 'have': have})
			self.myAgent.send(rep)

	def _setup(self):
		template = spade.Behaviour.ACLTemplate()
		template.addReceiver(spade.AID.aid("tracker@"+host, ["xmpp://tracker@"+host]))
		tmp = spade.Behaviour.MessageTemplate(template)
		self.addBehaviour(self.TrackerBehaviour(), tmp)

# execution
if __name__ == "__main__":

	tracker = TrackerAgent("tracker@"+ host, "secret")
	tracker.wui.start()
	tracker.start()

	alive = True
	while alive:
		try: time.sleep(1) 
		except KeyboardInterrupt: alive=False

	tracker.stop()