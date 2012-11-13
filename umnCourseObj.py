#!/usr/bin/python

class UmnCourse:
	def __init__(self, subj, num, desc):
		self.sectionDict = {}
		self.subj = str(subj)
		self.num = str(num)
		self.desc = str(desc)
	def __repr__(self):
		if self.getNumSections() == 1:
			pluralText = 'section'
		else:
			pluralText = 'sections'
		return self.subj + ' ' + str(self.num) + ': ' + self.desc + ' (' + str(self.getNumSectionsOpen()) + ' of ' + str(self.getNumSections()) + ' ' + pluralText + ' open)'
	def addSection(self, sectionNum, sectionData):
		self.sectionDict[sectionNum] = sectionData
	def delSection(self, sectionNum):
		del self.sectionDict[sectionNum]
	def getSection(self, sectionNum):
		return self.sectionDict[sectionNum]
	def getAllSections(self):
		return self.sectionDict
	def getCourseSubj(self):
		return self.subj
	def getCourseNum(self):
		return self.num
	def getCourseId(self):
		return self.subj + ' ' + self.num
	def getCourseDesc(self):
		return self.desc
	def getNumSections(self):
		return len(self.sectionDict)
	def getNumSectionsClosed(self):
		sectionsClosed = 0
		for section in self.sectionDict:
			if self.sectionDict[section].isClosed:
				sectionsClosed += 1
		return sectionsClosed
	def getNumSectionsOpen(self):
		return self.getNumSections() - self.getNumSectionsClosed()
	def getCourseLevel(self):
		try:
			return int(self.num[0])
		except:
			return -1

class UmnSection:
	def __init__(self, num, seatsOpen = 0, seatsTotal = 0, isClosed = False):
		self.num = int(num)
		self.seatsOpen = int(seatsOpen)
		self.seatsTotal = int(seatsTotal)
		self.isClosed = isClosed
		self.waitlist = ''
	def __repr__(self):
		if self.waitlist == 'Closed':
			wlOpenStr = ' (Waitlist closed)'
		elif self.waitlist == 'NotYetOpen':
			wlOpenStr = ' (Waitlist will open when class fills)'
		elif self.waitlist == 'Open':
			wlOpenStr = ' (Waitlist open)'
		else:
			wlOpenStr = ''
		if self.isClosed:
			return 'Section ' + str(self.num) + ' (Closed)' + wlOpenStr
		else:
			return 'Section ' + str(self.num) + ' (' + str(self.seatsOpen) + '/' + str(self.seatsTotal) + ' seats open)' + wlOpenStr
	def setSectionClosed(self):
		self.isClosed = True
	def setSectionOpen(self):
		self.isClosed = False
	def setWaitlistClosed(self):
		self.waitlist = 'Closed'
	def setWaitlistOpen(self):
		self.waitlist = 'Open'
	def setWaitlistNotYetOpen(self):
		self.waitlist = 'NotYetOpen'
	def setWaitlistUndefined(self):
		self.waitlist = ''
	def isClosed(self):
		return self.isClosed
	def waitlistClosed(self):
		return self.waitlist == 'Closed'
	def setSeatsOpen(self, num):
		self.seatsOpen = int(num)
	def setSeatsTotal(self, num):
		self.seatsTotal = int(num)
	def getSeatsOpen(self):
		return int(self.seatsOpen)
	def getSeatsTotal(self):
		return int(self.seatsTotal)
	def getSeatsFilled(self):
		return int(self.seatsTotal) - int(self.seatsOpen)