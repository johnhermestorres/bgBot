# bgBot.py

import os
from flask import Flask, request, Response
from twilio import twiml
from twilio.rest import TwilioRestClient

from scheduler import Scheduler


TWILIO_NUMBER = os.environ.get('TWILIO_NUMBER', None)
USER_NUMBER = os.environ.get('USER_NUMBER', None)

app = Flask(__name__)
twilio_client = TwilioRestClient()
scheduler = Scheduler()


@app.route('/twilio', methods=['POST'])
def twilio_post():
	response = twiml.Response()
	# If I get a message from John...
	# if request.form['From'] == USER_NUMBER:
	# 	message = request.form['Body']
	# 	# do something with the message
	# 	print message

	# 	response_message = "sup bg admin"
	# 	twilio_client.messages.create(to=USER_NUMBER, from_=TWILIO_NUMBER,
	# 									body=response_message)

	# Message from anyone else
	message = request.form['Body']
	print message

	response_messages = scheduler.read_message(request.form['From'], message)
	for response_message in response_messages:
		# send responses -- the admin needs updates on everything
		twilio_client.messages.create(to=response_message.recipient,
										from_=TWILIO_NUMBER,
										body=response_message.message_content)

	return Response(response.toxml(), mimetype="text/xml"), 200


@app.route('/', methods=['GET'])
def test():
	return Response('It works!')

if __name__ == '__main__':
	app.run(debug=True)
