# guest.py

class Guest():
	def __init__(self, phoneNumber, lastName, firstName, status):
		self.phoneNumber = phoneNumber
		self.lastName    = lastName
		self.firstName   = firstName
		self.status      = status # INVITED/GOING/NOTGOING


	# 'phoneNumber', 'lastName', 'firstName', 'status'