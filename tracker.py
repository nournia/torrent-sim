import spade, time, random
host = '127.0.0.1'

class TrackerAgent(spade.Agent.Agent):
	class TrackerBehaviour(spade.Behaviour.EventBehaviour):
		def _process(self):
			msg = self._receive(True)
			print "received message: ", msg.getContent()

	def _setup(self):
		bhv = self.TrackerBehaviour()
		self.addBehaviour(bhv, None)

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