# scheduler.py 

# performs all bg dinner scheduling tasks

# takes a list of database users
# checks if anyone is supposed to be invited to this week's dinner
# sends them invitation, and waits for their response
# if they respond yes:
	# great! add them to the guest list
# no:
	# darn! hope we get you next time!

# import sqlite3
#from collections import namedtuple
import re, string, os
from message import Message
from guest import Guest

ADMIN_NUMBER = os.environ.get('USER_NUMBER', None)
#ADMIN_NUMBER = "+17607167290"

# Message templates
MESSAGE_GREETING = '''
Hey {0}!
I'm bgBot -- the beer garden's assistant.
(In reality, we just make Andy send these texts against his will)
If you ever hear from me, it's probably because we wanted to invite you to bg dinner, go ball, or a pregame.
Hope to see you soon!
'''

MESSAGE_DINNER_INVITE = '''
{0}! I heard you're free this Wednesday. I also heard that you like to eat dank food.
If both of these are true, are you down for bg dinner this Wednesday, 7:30PM?
You can respond with yes, no, or "Scott sucks".
'''

MESSAGE_DINNER_INVITE_YES_RESPONSE = '''YES! So stoked to see you at dinner!'''
MESSAGE_DINNER_INVITE_NO_RESPONSE  = '''Bummer! Raincheck for sure then!'''
MESSAGE_ERROR_MESSAGE = "Whoa {0}, what do you mean by that? No but for real, I didn't understand what you mean when you said:\n{1}"

class Scheduler():

	def __init__(self):
		self.guest_list = []

	def read_message(self, sender, message):
		# print "message: ", message
		if sender == ADMIN_NUMBER:
			message_data = message.split(";")
			if message_data[0] == "ADD": # messsage types: ADD, DINNER_INVITE, BALL_INVITE
				# send them the initial greeting
				# message = "ADD;7607167290;John;Torres"
				guest = Guest(message_data[1],
								message_data[3],
								message_data[2],
								"")
				response_messages = self.add_guest(guest)

			elif message_data[0] == "DINNER_INVITE":
				# message = "DINNER_INVITE;7607167290;John;Torres"
				guest = Guest(message_data[1],
								message_data[3],
								message_data[2],
								"INVITED")
				response_messages = self.invite_guest(guest)

			elif message_data[0] == "BALL_INVITE":
				pass
			else:
				print "Sender number: ", sender
				response_messages = self.send_admin_error_message(message)
		else:
			if any(g.phoneNumber == sender.strip('+') for g in self.guest_list): # check if the sender is in the guestlist:
				# search for guest in the list
				for g in self.guest_list:
					if g.phoneNumber == sender.strip('+'):
						guest = g

				rsvp_answer = self._interpret_rsvp(message)
				if rsvp_answer == "YES":
					response_messages = self.confirm_guest_going(guest)
				elif rsvp_answer == "NO":
					response_messages = self.confirm_guest_not_going(guest)
				else:
					response_messages = self.send_error_message(guest, message)

			else:
				response_messages = self.send_unrecognized_number_message(sender, message)

		return response_messages


	# def create_response(self, recipient, message):
	# 	response = 

	def add_guest(self, guest):
		response_messages = []

		# Greet the new guest for the first time
		message_body = MESSAGE_GREETING.format(guest.firstName)
		response_message = Message(guest.phoneNumber, message_body)
		response_messages.append(response_message)

		# send notification to admin that they've been greeted
		message_body = "Added (greeted): {0} {1}".format(guest.firstName, guest.lastName)
		response_message = Message(ADMIN_NUMBER, message_body)
		response_messages.append(response_message)

		print message_body
		return response_messages

	def confirm_guest_going(self, guest):
		response_messages = []
		# Send message to guest
		message_body = MESSAGE_DINNER_INVITE_YES_RESPONSE
		response_message = Message(guest.phoneNumber, message_body)
		response_messages.append(response_message)

		# Notify admin
		message_body = "Guest {0} {1} confirmed GOING".format(guest.firstName, guest.lastName)
		response_message = Message(ADMIN_NUMBER, message_body)
		response_messages.append(response_message)

		print message_body
		return response_messages

	def confirm_guest_not_going(self, guest):
		response_messages = []
		# Send message to guest
		message_body = MESSAGE_DINNER_INVITE_NO_RESPONSE
		response_message = Message(guest.phoneNumber, message_body)
		response_messages.append(response_message)

		# Notify admin
		message_body = "Guest {0} {1} confirmed NOTGOING".format(guest.firstName, guest.lastName)
		response_message = Message(ADMIN_NUMBER, message_body)
		response_messages.append(response_message)

		print message_body
		return response_messages

	def send_error_message(self, guest, message):
		response_messages = []

		# Error message to guest
		message_body = MESSAGE_ERROR_MESSAGE.format(guest.firstName, message)
		response_message = Message(guest.phoneNumber, message_body)
		response_messages.append(response_message)

		# Notify admin of error message
		message_body = "Error reading message from {0} {1}\nMessage: {2}".format(guest.firstName, guest.lastName, message)
		response_message = Message(ADMIN_NUMBER, message_body)
		response_messages.append(response_message)

		print message_body
		return response_messages

	def send_admin_error_message(self, message):
		response_messages = []

		# Notify admin of error message
		message_body = "Error reading admin message: {0}".format(message)
		response_message = Message(ADMIN_NUMBER, message_body)
		response_messages.append(response_message)

		print message_body
		return response_messages

	def send_unrecognized_number_message(self, sender, message):
		response_messages = []

		# Notify admin of unrecognized number
		message_body = "Message received from unknown sender.\nSender: {0}\nMessage: {1}".format(sender, message)
		response_message = Message(ADMIN_NUMBER, message_body)
		response_messages.append(response_message)

		print message_body
		return response_messages

	def invite_guest(self, guest):
		self.guest_list.append(guest)		
		response_messages = []

		# Invite the guest
		message_body = MESSAGE_DINNER_INVITE.format(guest.firstName)
		response_message = Message(guest.phoneNumber, message_body)
		response_messages.append(response_message)

		# Notify admin
		message_body = "Invited guest: {0} {1}".format(guest.firstName, guest.lastName)
		response_message = Message(ADMIN_NUMBER, message_body)
		response_messages.append(response_message)

		print message_body
		return response_messages

	def _interpret_rsvp(self, rsvp):
		# TODO: use NLP for sentiment analysis
		clean_rsvp_string = rsvp.lower()
		pattern = re.compile('[\W_]+')
		clean_rsvp_string = pattern.sub('', clean_rsvp_string) # remove alphanumeric

		affirmative_answers = ["yes", "yep", "yeah", "scottsucks"]
		negative_answers = ["no", "nah", "nope", "cant", "sorry"]

		# do something for Scott sucks

		if any(answer in clean_rsvp_string for answer in affirmative_answers):
			return "YES"
		elif any(answer in clean_rsvp_string for answer in negative_answers):
			return "NO"
		else:
			return "ERROR"


	#def _fill_update_template()

if __name__ == '__main__':
	print "Welcome to bgBot.scheduler\n"
	scheduler = Scheduler()