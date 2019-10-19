"""
Shafayat R
FSU Parking Updates
2017 June 28
"""

#from __future__ import print_function

from datetime import date
import datetime
import re

# Import the necessary package to process data in JSON format
try:
	import json
except ImportError:
	import simplejson as json

#Improt necessary methods from the "twitter" library
from twitter import Twitter, OAuth, TwitterHTTPError, TwitterStream

# Obfuscated for security reasons. 
ACCESS_TOKEN = '#####'
ACCESS_SECRET = '#####'
CONSUMER_KEY = '#####'
CONSUMER_SECRET = '#####'
	

# --------------- Main handler ------------------

def lambda_handler(event, context):
	""" Route the incoming request based on type (LaunchRequest, IntentRequest,
	etc.) The JSON body of the request is provided in the event parameter.
	"""
	print("event.session.application.applicationId=" + event['session']['application']['applicationId'])

	"""
	Uncomment this if statement and populate with your skill's application ID to
	prevent someone else from configuring a skill that sends requests to this
	function.
	"""
	if (event['session']['application']['applicationId'] != "amzn1.ask.skill.e033c9a3-4b8d-46aa-8564-442ccee45b2b"):
		raise ValueError("Invalid Application ID")

	if event['session']['new']:
		on_session_started({'requestId': event['request']['requestId']}, event['session'])

	if event['request']['type'] == "LaunchRequest":
		return on_launch(event['request'], event['session'])
	elif event['request']['type'] == "IntentRequest":
		return on_intent(event['request'], event['session'])
	elif event['request']['type'] == "SessionEndedRequest":
		return on_session_ended(event['request'], event['session'])


# --------------- Helpers that build all of the responses ----------------------
def build_speechlet_response(title, output, reprompt_text, should_end_session):
	return {
		'outputSpeech': {
			'type': 'PlainText',
			'text': output
		},
		'card': {
			'type': 'Simple',
			'title': title,
			'content': output
		},
		'reprompt': {
			'outputSpeech': {
				'type': 'PlainText',
				'text': reprompt_text
			}
		},
		'shouldEndSession': should_end_session
	}


def build_response(session_attributes, speechlet_response):
	return {
		'version': '1.0',
		'sessionAttributes': session_attributes,
		'response': speechlet_response
	}


# --------------- Functions that control the skill's behavior ------------------

def get_welcome_response():
	""" If we wanted to initialize the session to have some attributes we could
	add those here
	"""

	session_attributes = {}
	card_title = "Welcome"
	speech_output = "Welcome to F. S. U. Parking Updates Application. Please ask me for transportation updates by saying, updates for today."

	# If the user either does not reply to the welcome message or says something
	# that is not understood, they will be prompted again with this text.
	reprompt_text = "Please ask me for transportation updates by saying, updates for today."
	should_end_session = False
	return build_response(session_attributes, build_speechlet_response(card_title, speech_output, reprompt_text, should_end_session))


def handle_session_end_request():
    card_title = "Goodbye!"
    speech_output = "Thank you for trying the F. S. U. Parking Updates Application. Have a nice day! "
    should_end_session = True
    return build_response({}, build_speechlet_response(card_title, speech_output, None, should_end_session))


# --------------- Events ------------------

def on_session_started(session_started_request, session):
	""" Called when the session starts """

	print("on_session_started requestId=" + session_started_request['requestId'] + ", sessionId=" + session['sessionId'])


def on_launch(launch_request, session):
	""" Called when the user launches the skill without specifying what they
	want
	"""

	print("on_launch requestId=" + launch_request['requestId'] + ", sessionId=" + session['sessionId'])
	# Dispatch to your skill's launch
	return get_welcome_response()


def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """
    
    print("on_intent requestId=" + intent_request['requestId'] + ", sessionId=" + session['sessionId'])
    
    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']
    
    if intent_name == "GetTodaysUpdates":
        return func_for_today(intent, session)
    elif intent_name == "GetTomorrowsUpdates":
        return func_for_tomorrow(intent, session)
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        raise ValueError("Invalid intent")


def on_session_ended(session_ended_request, session):
	""" Called when the user ends the session.

	Is not called when the skill returns should_end_session=true
	"""
	print("on_session_ended requestId=" + session_ended_request['requestId'] + ", sessionId=" + session['sessionId'])
	# add cleanup logic here


def func_for_today(intent, session):
	""" Grabs our bus times and creates a reply for the user
	"""
 
	card_title = "Transportation updates for today"
	session_attributes = {}
	should_end_session = True

	ParkingUpdates, SeminoleExpressUpdates, OtherUpdates = get_tweets_of_user_for_today()
	resultText = print_output(ParkingUpdates, SeminoleExpressUpdates, OtherUpdates, "today")

	if len(resultText) != 0:
		speech_output = resultText

		reprompt_text = ""
    
	else:
		reprompt_text = "Please ask me for transportation updates by saying, updates for today."
		speech_output = "Please ask me for transportation updates by saying, updates for today."
        
	return build_response(session_attributes, build_speechlet_response(card_title, speech_output, reprompt_text, should_end_session))


def func_for_tomorrow(intent, session):
	""" Grabs our bus times and creates a reply for the user
	"""

	card_title = "Transportation updates for tomorrow"
	session_attributes = {}
	should_end_session = True

	ParkingUpdates, SeminoleExpressUpdates, OtherUpdates = get_tweets_of_user_for_tomorrow()
	resultText = print_output(ParkingUpdates, SeminoleExpressUpdates, OtherUpdates, "tomorrow")

	if len(resultText) != 0:
		speech_output = resultText
		reprompt_text = ""
	else:
		reprompt_text = "Please ask me for transportation updates by saying, updates for today."
		speech_output = "Please ask me for transportation updates by saying, updates for today."
        
	return build_response(session_attributes, build_speechlet_response(card_title, speech_output, reprompt_text, should_end_session))

def get_tweets_of_user_for_today():
    
	oauth = OAuth(ACCESS_TOKEN, ACCESS_SECRET, CONSUMER_KEY, CONSUMER_SECRET)

	
	twitter = Twitter(auth=oauth)

	iterator = twitter.statuses.user_timeline(screen_name="FSUParking", exclude_replies = "true")

	ParkingUpdates = []
	SeminoleExpressUpdates = []
	OtherUpdates = []
	
	for tweet in iterator:
		#print("\n\n\n------------------------------------------\n\n")
		#print(json.dumps(tweet))
		#print(json.dumps(tweet, indent=4)) #for pretty printing
		if "text" in tweet:
			if is_it_todays_tweet(tweet["text"]):
				cat = caterogrize_tweet(tweet)
				if cat == 1:
					ParkingUpdates.append(tweet)
				elif cat == 2:
					SeminoleExpressUpdates.append(tweet)
				else:
					OtherUpdates.append()
	
	return ParkingUpdates, SeminoleExpressUpdates, OtherUpdates

def get_tweets_of_user_for_tomorrow():
	
	oauth = OAuth(ACCESS_TOKEN, ACCESS_SECRET, CONSUMER_KEY, CONSUMER_SECRET)

	twitter = Twitter(auth=oauth)

	iterator = twitter.statuses.user_timeline(screen_name="FSUParking", exclude_replies = "true")
	
	ParkingUpdates = []
	SeminoleExpressUpdates = []
	OtherUpdates = []
	
	for tweet in iterator:
		#print("\n\n\n------------------------------------------\n\n")
		#print(json.dumps(tweet))
		#print(json.dumps(tweet, indent=4)) #for pretty printing
		if "text" in tweet:
			if is_it_tomorrows_tweet(tweet["text"]):
				cat = caterogrize_tweet(tweet)
				if cat == 1:
					ParkingUpdates.append(tweet)
				elif cat == 2:
					SeminoleExpressUpdates.append(tweet)
				else:
					OtherUpdates.append()
	
	return ParkingUpdates, SeminoleExpressUpdates, OtherUpdates

	
def print_output(ParkingUpdates, SeminoleExpressUpdates, OtherUpdates, dayText):	
	'dayText can be "today" or "tomorrow" '
	
	resultText = ""
	
	if (dayText == "tomorrow"):
		if len(ParkingUpdates) == 0 and len(SeminoleExpressUpdates) == 0 and len(OtherUpdates) == 0:
			#print("There are no transportation updates for {}.".format(dayText))
			resultText += "There is no transportation update for {}.\n".format(dayText)
			resultText += "This generally means normal service will be in effect. Please check again this evening or tomorrow morning to see if any new update is posted."
			return resultText

	if (dayText == "today"):
		if len(ParkingUpdates) == 0 and len(SeminoleExpressUpdates) == 0 and len(OtherUpdates) == 0:
			#print("There are no transportation updates for {}.".format(dayText))
			resultText += "There is no transportation update for {}.\n".format(dayText)
			resultText += "This generally means normal service is in effect. Please check again later to see if any new update is posted."
			return resultText


	
	#print("There are {} parking updates, {} Seminol Express updates and {} other updates for {}.".format(len(ParkingUpdates), len(SeminoleExpressUpdates), len(OtherUpdates), dayText))
	AA = ""
	BB = ""
	CC = ""
	
	if len(ParkingUpdates) > 1:
		AA = "s"
	if len(SeminoleExpressUpdates) > 1:
		BB = "s"
	if len(OtherUpdates) > 1:
		CC = "s"
	
	resultText += "There are {} parking update{}, {} Seminole Express update{} and {} other update{} for {}.\n".format(len(ParkingUpdates), AA, len(SeminoleExpressUpdates), BB, len(OtherUpdates), CC, dayText)
	
	if len(ParkingUpdates) > 0:
		#print("Parking updates are: ")
		#resultText += "Parking updates are: \n"
		for tweet in ParkingUpdates:
			text = tweet["text"]
			text = text.replace("-", "to")
			
			resultText += text + "\n"
			
	if len(SeminoleExpressUpdates) > 0:
		#print("Seminole Express updates are: ")
		#resultText += "Seminole Express updates are: \n"
		for tweet in SeminoleExpressUpdates:
			text = tweet["text"]
			text = text.replace("-", "to")
			
			resultText += text + "\n"
			
	if len(OtherUpdates) > 0:
		#print("Other updates are: ")
		#resultText += "Other updates are: \n"
		for tweet in OtherUpdates:
			text = tweet["text"]
			text = text.replace("-", "to")
			
			resultText += text + "\n"
			
	#print("End of updates.")
	resultText += "End of updates. \n"
	
	#resultText += "current time is: {} {} {} {} {} {} \n".format(datetime.datetime.now().year, datetime.datetime.now().month, datetime.datetime.now().day, datetime.datetime.now().hour, datetime.datetime.now().minute, datetime.datetime.now().second)
	
	return resultText
		
	pass
	
	
def print_tweet(tweet):
	#print(tweet["id"])
	#print(tweet["created_at"])
	print(tweet["text"])
	#print(tweet["user"]["id"])
	#print(tweet["user"]["name"])
	#print(tweet["user"]["screen_name"])
	
	#hashtags = []
	#for hashtag in tweet["entities"]["hashtags"]:
	#	hashtags.append(hashtag["text"])
	
	#print(hashtags)
	
	#print("____________________")
	#print(json.dumps(tweet, indent=4))
	pass

def is_it_todays_tweet(tweet):	
	'right now it is only matching the date in tweet text.'
	'should expand to consider creation date as well.'
	desiredDate = convert_text_to_date("today")
	desiredMonth, desiredDay = desiredDate

	t_day = -1
	t_month = -1

	pattern = re.compile("\d+/\d+")
	matches = pattern.findall(tweet)
		
	if len(matches) == 1:
		tweetdate = matches[0]
		#print("tweet date: ",tweetdate)
		t_month = int(tweetdate[:tweetdate.find("/")])		
		t_day = int(tweetdate[tweetdate.find("/")+1 : ])
			
		if (desiredMonth == t_month) and (desiredDay == t_day):
			return True
	else:
		return False		
			
	pass
	
def is_it_tomorrows_tweet(tweet):	
	desiredDate = convert_text_to_date("tomorrow")
	desiredMonth, desiredDay = desiredDate

	t_day = -1
	t_month = -1

	pattern = re.compile("\d+/\d+")
	matches = pattern.findall(tweet)
		
	if len(matches) == 1:
		tweetdate = matches[0]
		#print("tweet date: ",tweetdate)
		t_month = int(tweetdate[:tweetdate.find("/")])		
		t_day = int(tweetdate[tweetdate.find("/")+1 : ])
			
		if (desiredMonth == t_month) and (desiredDay == t_day):
			return True
	else:
		return False		
			
	pass


	
def caterogrize_tweet(tweet):
	'''
	tweets can be:
		1. today's parking update (cat 1)
		2. today's seminole express update (Cat 2)
		3. today's any other update (cat 3)
		4. older tweet that cover today's date (cat 4) 
	'''
	
	if "parking update" in tweet["text"].lower():
		return 1
	elif "seminole express update" in tweet["text"].lower():
		return 2 
	else:
		return 3
	pass	
	
def get_time():
	year = date.today().year
	month = date.today().month
	day = date.today().day
	
	'sample format: 6/22 Parking Update: 8 AM - 12 PM, 80 spaces in the Alumni Center are reserved.'
	tweet = r"6/22 - 6/23 Parking Update: 8 AM - 12 PM, 80 spaces in the Alumni Center are reserved."
	pattern = re.compile("\d+/\d+")
	matches = pattern.findall(tweet)
	
	if len(matches) == 1:
		tweetdate = matches[0]
		print("tweet date: ",tweetdate)
	
	elif len(matches) == 2:
		startdate = matches[0]
		enddate = matches[1]
		print("start date: ",startdate)
		print("end date: ",enddate)
	
def is_it_last_day_of_month(month,day):
	months = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
	
	year = date.today().year
	if year % 400 == 0:
		months[1] = 29	#leap year
	elif year % 100 == 0:
		months[1] = 28	#not leap year
	elif year % 4 == 0:
		months[1] = 29	#leap year
	
	if day == months[month-1]:
		return True
	else:
		return False
	
	pass	
	
def rollback_a_day(month, day):
	months = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
	
	year = date.today().year
	if year % 400 == 0:
		months[1] = 29	#leap year
	elif year % 100 == 0:
		months[1] = 28	#not leap year
	elif year % 4 == 0:
		months[1] = 29	#leap year

	if day == 1:
		month -= 1
		day = months[month-1]
	else:
		day -= 1
		
	return (month, day)

	pass
	
def convert_text_to_date(text):
	'text can be today or tomorrow'
	
	'AWS servers follow UTC time. -5 hrs seems a safe adjustment. Can worry about proper DST adjustment later.'
	
	hour = datetime.datetime.now().hour
	 
	
	if text.lower() == "today":
		month = date.today().month
		day = date.today().day
				
		desiredDate = (month, day)
		
		if hour < 5:
			desiredDate = rollback_a_day(month, day)
			
	elif text.lower() == "tomorrow":
		month = date.today().month
		day = date.today().day
		
		if is_it_last_day_of_month(month,day):
			month += 1			
			if month == 13:
				month = 1
			day = 1
		else:
			day += 1
		desiredDate = (month, day)
		
		if hour < 5:
			desiredDate = (date.today().month, date.today().day)	#tomorrow becomes today
		
		
	else:
		desiredDate = None
		
	return desiredDate	
	pass


if __name__ == "__main__":
	print("Hello World!")
	ParkingUpdates, SeminoleExpressUpdates, OtherUpdates = get_tweets_of_user_for_tomorrow()
	resultText = print_output(ParkingUpdates, SeminoleExpressUpdates, OtherUpdates, "tomorrow")
	print(resultText)
	
	ParkingUpdates, SeminoleExpressUpdates, OtherUpdates = get_tweets_of_user_for_today()
	resultText = print_output(ParkingUpdates, SeminoleExpressUpdates, OtherUpdates, "today")
	print(resultText)

