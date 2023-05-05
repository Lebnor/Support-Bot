import json
import os
import string
import sys
import traceback

from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk
nltk.data.path.append("/tmp")
from googletrans import Translator

translator = Translator(service_urls=['translate.googleapis.com'])

here = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(here, "./vendored"))

import requests

TOKEN = os.environ['API_KEY']
BASE_URL = f"https://api.telegram.org/bot{TOKEN}"
CHAT_ID = os.environ['CHAT_ID']
OWN_ID = os.environ['OWN_ID']
LIELS_BOT_TESTING_PLAYGROUND_ID = os.environ['LIELS_BOT_TESTING_PLAYGROUND_ID']
PRIVATE_PLAYGROUND = os.environ['PRIVATE_PLAYGROUND']
S = os.environ['S']

admin_group_id = -652463766 # החברים הטובים מנהלים

# Translate all 8 emotions for sentiment analysis
def emotion_to_he(emotion):
    if emotion == "anger":
        return "כעס"
    elif emotion == "disgust":
        return "גועל"
    elif emotion == "fear":
        return "פחד"
    elif emotion == "joy":
        return "הנאה"
    elif emotion == "sadness":
        return "עצב"
    elif emotion == "surprise":
        return "הפתעה"
    elif emotion == "trust":
        return "אמון"
    return ""

def detect_language(text):
    heb_score = 0
    eng_score = 0
    for char in text:
        char = char.lower()
        if char > 'a' and char < 'z':
            eng_score += 1
        elif char > 'א' and char < 'ת':
            heb_score += 1
    return "he" if heb_score > eng_score else "en"


# Bot recieved regular text message
def handle_message(data):

    # get message object
    message = data['message']
    
    chat = message['chat']
    chat_id = chat['id']

    

    response = ""
    type = chat['type']

    if type == 'private':
        # set bot is typing status
        set_typing_url = BASE_URL + "/sendChatAction"
        requests.post(set_typing_url, { "chat_id": chat_id, "action": "typing" })
        try:
            res = requests.get(BASE_URL + f"/getFullChat?chat_id={-1001343843558}")
            requests.post(BASE_URL + "/sendMessage", { "chat_id":  OWN_ID, "text": res})
        except:
            pass
        if 'from' in message:
            _from = message['from']
            first_name = _from['first_name']
        
        emotions = ''
        if 'text' in message: # it was a regular text message
            text = message['text']
            # detect language user typed in
            lang = detect_language(text)

            written_lang = 'עברית' if lang == 'he' else 'אנגלית'
            response = f"תודה {first_name}, הודעתך ב{written_lang} התקבלה.\n"
            response += "\n"
            
            if lang == "he":
                response += "מצטער, עברית לא נתמכת כרגע.\nאנא נסו שוב באנגלית."
            else:
                # analyze sentiment
                nltk.download('vader_lexicon', download_dir='/tmp')
                
                # general emotions - positive/negative
                sid = SentimentIntensityAnalyzer()
                emotions = sid.polarity_scores(text)
                compound = emotions['compound']
                if compound > 0.5:
                    emotions = '*חיובי מאוד* 😃'
                elif compound > 0.1:
                    emotions = '*חיובי* 🙂'
                elif compound > -0.1:
                    emotions = '*נייטרלי* 😐'
                elif compound > -0.5:
                    emotions = '*שלילי* 🙁'
                else:
                    emotions = '*שלילי מאוד* 😭'
                response += f"הרגש שהבעת: {emotions}"
                try:
                    nltk.download('punkt', download_dir='/tmp')
                    from nrclex import NRCLex
                    top_emotions = NRCLex(text).top_emotions
                    
                    # detailed emotions
                    details = "\nפירוט רגשות עיקריים שהבעת:\n"
                    found_emotion = False
                    for emotion, score in top_emotions:
                        translated_emotion = emotion_to_he(emotion)
                        if score == 0 or not translated_emotion:
                            continue
                        found_emotion = True
                        percentage = f"{round( (1 / score), 1 )}%"
                        details += f"*{emotion_to_he(emotion)}*: {percentage}\n"
                    if found_emotion:
                        response += details
                except Exception as e:
                    print(e)
                    pass

    elif type == 'group':
        # todo handle bot responses to group messages
        if 'text' in message:
            text = message['text']
        if 'from' in message:
            _from = message['from']
            user_name = _from['username']
        response = ""
        chat_id = OWN_ID
    print("The response", response)
    return {"response": response, "chat_id": chat_id}

def handle_callback(data):
    pass
def handle_inline_query(data):
    pass
def handle_chosen_inline_result(data):
    pass
def handle_shipping_query(data):
    pass
def handle_pre_checkout_query(data):
    pass
def handle_poll(data):
    pass
def handle_poll_answer(data):
    pass
def handle_shipping_query(data):
    pass
def handle_pre_checkout_query(data):
    pass
def handle_edited_message(data):
    pass
def handle_edited_channel_post(data):
    pass
def handle_channel_post(data):
    pass
def handle_my_chat_member(data):
    pass
def handle_chat_member(data):
    chat_member_obj = data['chat_member']
    user = chat_member_obj['user']
    response = {"response": f"{user} עזב את הצ'אט", "chat_id": admin_group_id}
    return response 

def handle_chat_join_request(data):
    pass

def hello(event, context):

  
    res = 200
    try:
        data = json.loads(event['body'])
        if 'message' in data:
            res = handle_message(data)
        elif 'callback_query' in data:
            res = handle_callback(data)
        elif 'edited_message' in data:
            res = handle_edited_message(data)
        elif 'edited_channel_post' in data:
            res = handle_edited_channel_post(data)
        elif 'channel_post' in data:
            res = handle_channel_post(data)
        elif 'inline_query' in data:
            res = handle_inline_query(data)
        elif 'chosen_inline_result' in data:
            res = handle_chosen_inline_result(data)
        elif 'callback_query' in data:
            res = handle_callback(data)
        elif 'shipping_query' in data:
            res = handle_shipping_query(data)
        elif 'pre_checkout_query' in data:
            res = handle_pre_checkout_query(data)
        elif 'poll' in data:
            res = handle_poll(data)
        elif 'poll_answer' in data:
            res = handle_poll_answer(data)
        elif 'my_chat_member' in data:
            res = handle_my_chat_member(data)
        elif 'chat_member' in data:
            res = handle_chat_member(data)
        elif 'chat_join_request' in data:
            res = handle_chat_join_request(data)
        

    except Exception as e:
        print("There was an error!")
        print("the exception:")
        print(traceback.format_exc())
        print(e)
        res = 500
    
    if res:
        response = res['response'] if "response" in res else "סליחה, אני לא יודע מה לענות על זה"
        chat_id = res['chat_id'] if "chat_id" in res else OWN_ID
    else:
        response = "סליחה, אני לא יודע מה לענות על זה"
        chat_id = OWN_ID
    data = {"text": response.encode("utf8"), "chat_id": chat_id}
    url = BASE_URL + "/sendMessage?parse_mode=Markdown"
    requests.post(url, data)

    return {"statusCode": 200}
