import sigrokdecode as srd

class Decoder(srd.Decoder):
	api_version = 2
	id = 'vive'
	name = 'Vive'
	longname = 'Vive lighthouse decoder'
	desc = 'Decodes the signals used i Vive lighthouse tracking'
	license = 'gplv4+'
	inputs = ['ir']
	outputs = ['angles']
	channels = ( 
		{'id' : 'data', 'name' : 'Data', 'desc' : 'Digital data from photodiode'},
	)	
	annotations = (
		('lighthouse', 'Lighthouse'),
		('ootx', 'OOTX'),
	)
	annotation_rows = (
		('lighthouse', 'Lighthouse', (0,)),
		('ootx', 'OOTX', (1,)),
	)

	def putangle(self, lhouse, axis, time):
		self.put(self.syncstart, self.edge, self.out_ann, [0, ['%s, %i, %.6f' % (lhouse, axis, time/8333*3.1459)]])

	def samples_to_us(self, samples): #converts number of samples to microseconds
		seconds = samples/self.samplerate
		return (seconds*1000000)
	
	def __init__(self, **kwargs):
		self.olddata = None
		self.edge = 0
		self.pulselength = 0
		self.syncstart = 0
		self.insweep = 0
		self.lighthouse = "b"
		self.ootx = 0
		self.axis = 0
	
	def start(self):
 		self.out_ann = self.register(srd.OUTPUT_ANN)

	def metadata(self, key, value):
		if key == srd.SRD_CONF_SAMPLERATE:
			self.samplerate = value;


	def decode(self, ss, es, data):
		if self.samplerate is None:
			raise Exception("Unable to decode without samplerate.")

		for (self.samplenum, pins) in data:
			
			data = pins[0]
			
						
			if self.olddata == None:
				self.oldata = data
			
			if self.olddata == 0:
				self.edge = self.samplenum
				self.olddata = data
				continue
				
			if data == self.olddata:
	  		continue
			
			self.pulselength = self.samples_to_us(self.samplenum - self.edge) #calculates number of samples between last rising edge and now

			if self.pulselength <= 60:
				self.putangle(self.lighthouse, self.axis, self.samples_to_us(self.edge - self.syncstart))
				self.insweep = 0
			
			elif self.pulselength <= 100:
				self.syncstart = self.edge
			
				
				if self.insweep == 0:
					self.lighthouse = "b"
					self.insweep = 1
				else:
					self.lighthouse = "c"
					self.insweep = 0
				
				if self.pulselength <= 70:#j0
					self.axis = 0
					self.ootx = 0
				elif self.pulselength <= 80:#k0
					self.axis = 1
					self.ootx = 0
				elif self.pulselength <= 90:#j1
					self.axis = 0
					self.ootx = 1
				else:#k1
					self.axis = 0
					self.ootx = 1
				
			else:
				self.insweep = 1
			
			self.olddata = data
			self.pulselength = 0
