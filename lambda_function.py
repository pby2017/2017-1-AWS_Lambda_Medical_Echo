from __future__ import print_function
from twilio.rest import Client

account_sid = "account_sid"
auth_token = "auth_token"
client = Client(account_sid, auth_token)

# --------------- Helpers that build all of the responses ----------------------

def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': "SessionSpeechlet - " + title,
            'content': "SessionSpeechlet - " + output
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

    session_attributes = {}
    session_attributes["sayingType"] = ''
    session_attributes["answerCount"] = 0
    session_attributes["yesAnswerCount"] = 0

    card_title = "Welcome"
    speech_output = "Welcome to the dankoock I4S medical. " \
                    "Please tell me disease part by saying, " \
                    "cancer, heart, brain vessel, rare."

    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "Do not understand your saying." \
                    "Please tell me disease part by saying, " \
                    "cancer, heart, brain vessel, rare."
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def handle_session_end_request():
    card_title = "Session Ended"
    speech_output = "Thank you for trying the dankoock I4S medical. " \
                    "Have a nice day! "
    # Setting this to true ends the session and exits the skill.
    should_end_session = True
    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session))


def create_sore_part_attributes(sname, sore_part):
    return {sname: sore_part}

def strokeSurvey(sSCount):
    index = sSCount
    questionList = ["Half deadly",
                    "Sensory abnormality",
                    "Pronunciation disorder",
                    "Facial nerve palsy",
                    "Ataxia",
                    "Blindness",
                    "Diplopia",
                    "Difficulty in swallowing"]

    return questionList[index]


def diagnosis_in_session(intent, session):
    answerCountMax = 8
    sayingType = ''
    answerCount = 0
    yesAnswerCount = 0
    card_title = intent['name']

    if session["attributes"]:
        session_attributes = session["attributes"]
    else:
        session_attributes = {}
    if "BrainVessel" in session_attributes:
        sayingType = session["attributes"]["BrainVessel"]
    if "answerCount" in session_attributes:
        answerCount = session["attributes"]["answerCount"]
    else:
        session_attributes["answerCount"] = answerCount
    if "yesAnswerCount" in session_attributes:
        yesAnswerCount = session["attributes"]["yesAnswerCount"]
    else:
        session_attributes["yesAnswerCount"] = yesAnswerCount
    should_end_session = False

    if 'SurveyAnswer' in intent['slots']:
        sname = 'SurveyAnswer'
        surveyAnswer = intent['slots'][sname]['value']
        if surveyAnswer == 'yes':
            yesAnswerCount = yesAnswerCount + 1

        answerCount = answerCount + 1

        if sayingType == 'stroke':
            if answerCount < 8:
                speech_output = strokeSurvey(answerCount)
                speech_output = "Have you been " + speech_output \
                                +"? Saying yes or no."
                reprompt_text = "Do not understand your saying." \
                                + speech_output

            else:
                speech_output = "Your yes count is " + str(yesAnswerCount) \
                + ". If more than 1, recommand to visit near medical center."
                reprompt_text = "As repeat for saying, " + speech_output
                sayingType = ''
                answerCount = 0
                yesAnswerCount = 0
        else:
            speech_output = "This part is not supported now. " \
                            "Please saying open medi. " \
                            "And start at first stage. "
            reprompt_text = "Do not understand your saying. " \
                            + speech_output

    elif 'StartSurvey' in intent['slots']:
        sname = 'StartSurvey'
        surveyAnswer = intent['slots'][sname]['value']
        if surveyAnswer == 'ready':
            if sayingType == 'stroke':
                speech_output = strokeSurvey(answerCount)
                speech_output = "Have you been " + speech_output \
                                +"? Saying yes or no. "
                reprompt_text = "Do not understand your saying. " \
                                + speech_output
            else:
                speech_output = "This part is not supported now. " \
                                "Please saying open medi. " \
                                "And start at first stage. "
                reprompt_text = "Do not understand your saying. " \
                                + speech_output

        else:
            sayingType = ''
            answerCount = 0
            yesAnswerCount = 0
            speech_output = "OK"
            session_attributes["sayingType"] = sayingType
            session_attributes["answerCount"] = answerCount
            session_attributes["yesAnswerCount"] = yesAnswerCount
            return build_response(session_attributes, build_speechlet_response(
                card_title, speech_output, None, should_end_session))

    session_attributes["sayingType"] = sayingType
    session_attributes["answerCount"] = answerCount
    session_attributes["yesAnswerCount"] = yesAnswerCount

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def set_sorepart_in_session(intent, session):
    """ Sets the sorepart in the session and prepares the speech to reply to the
    user.
    """

    card_title = intent['name']

    if session["attributes"]:
        session_attributes = session["attributes"]
    else:
        session_attributes = {}

    should_end_session = False

    if 'Disease' in intent['slots']:
        sname = 'Disease'
        sore_part = intent['slots'][sname]['value']

        if not session_attributes:
            session_attributes = create_sore_part_attributes(sname, sore_part)
        else:
            session_attributes[sname] = sore_part

        if sore_part == 'brain vessel':
            speech_output = "You can say word for check your status. " \
                            "stroke, traumatic, spinal."
            reprompt_text = "Do not understand your saying. " \
                            + speech_output
        else:
            speech_output = "That word is not in service yet. " \
                            "Please saying another part. "
            reprompt_text = "Do not understand your saying. " \
                            + speech_output

    elif 'BrainVessel' in intent['slots']:
        sname = 'BrainVessel'
        sore_part = intent['slots'][sname]['value']

        if not session_attributes:
            session_attributes = create_sore_part_attributes(sname, sore_part)
        else:
            session_attributes[sname] = sore_part

        speech_output = "I will survey your status. " \
                        "Only answer yes or no. " \
                        "Now saying ready or not yet."
        reprompt_text = "Do not understand your saying. " \
                        + speech_output

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def help_me_in_session(intent, session):
    """ Sets the sorepart in the session and prepares the speech to reply to the
    user.
    """

    card_title = intent['name']

    if session["attributes"]:
        session_attributes = session["attributes"]
    else:
        session_attributes = {}

    should_end_session = False

    if 'HelpMe' in intent['slots']:
        sname = 'HelpMe'
        sore_part = intent['slots'][sname]['value']

        if not session_attributes:
              session_attributes = create_sore_part_attributes(sname, sore_part)
        else:
              session_attributes[sname] = sore_part

        if sore_part == 'help me':
            client.messages.create(
                to="+phone_number",
                from_="+twilio_phone_number",
                body="Owner fell down. Please help me - alexa.")

            speech_output = "Send Success"

            return build_response(session_attributes, build_speechlet_response(
                card_title, speech_output, None, True))

# --------------- Events ------------------

def on_session_started(session_started_request, session):
    """ Called when the session starts """

    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])


def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """

    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # Dispatch to your skill's launch
    return get_welcome_response()


def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """

    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # Dispatch to your skill's intent handlers
    if intent_name == "DiseasePartIsIntent" or intent_name == "DetailPartIsIntent":
        return set_sorepart_in_session(intent, session)
    elif intent_name == "YesOrNoIntent" or intent_name == "ReadyOrNotYetIntent":
        return diagnosis_in_session(intent, session)
    elif intent_name == "HelpMeIntent":
        return help_me_in_session(intent, session)
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
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # add cleanup logic here


# --------------- Main handler ------------------

def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])

    """
    Uncomment this if statement and populate with your skill's application ID to
    prevent someone else from configuring a skill that sends requests to this
    function.
    """
    # if (event['session']['application']['applicationId'] !=
    #         "amzn1.echo-sdk-ams.app.[unique-value-here]"):
    #     raise ValueError("Invalid Application ID")

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])
