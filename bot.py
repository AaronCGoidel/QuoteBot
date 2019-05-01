import websocket
import json
import requests
import os
import sys
import logging
import time
import datetime as dt
import random

logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)


TOKEN = os.environ["SLACK_API_TOKEN"]
QUOTE_URL = os.environ["QUOTE_FETCH_URL"]
SEND_GREETING = os.environ["SEND_GREETING"]

def getName(id):
  logging.debug('requesting name of id: ' + id)
  users = requests.get("https://slack.com/api/users.list?token=" + TOKEN).json()

  for elt in users['members']:
    if elt['id'] == id:
      name = elt['real_name']
      logging.debug('name found: ' + name)
      return name
    else: 
      logging.debug('no name found')

def start_rtm():
  req = requests.get("https://slack.com/api/rtm.start?token="+TOKEN, verify=False).json()
  # logging.info(req)

  return req['url']

def sendMessage(fact, user_id):
  user_info = requests.get("https://slack.com/api/im.open?token="+TOKEN+"&user="+user_id).json()
  CHANNEL = user_info["channel"]["id"]

  message_data = {
    'token': TOKEN,
    'channel': CHANNEL,
    'parse': 'full',
    'text': fact,
    'as_user': 'true'

  }
  post = requests.post("https://slack.com/api/chat.postMessage", data=message_data)
  logging.info("Sent Message")
  return True

def sendGreeting(user_id):
  user_info = requests.get("https://slack.com/api/im.open?token="+TOKEN+"&user="+user_id).json()
  CHANNEL = user_info["channel"]["id"]
  greeting = "Hello, " + getName(user_id) + ". "
  body = "Thank you for subscribing to CAT FACTS! " + "You will receive one random interesting feline fact every hour."
  message = greeting + body

  message_data = {
    'token': TOKEN,
    'channel': CHANNEL,
    'parse': 'full',
    'text': message,
    'as_user': 'true'

  }
  post = requests.post("https://slack.com/api/chat.postMessage", data=message_data)
  logging.info("Greeting Sent")
  return True

def on_open(ws):
  logging.info("\033[32m"+"Connection Opened"+"\033[0m" + ", messages will be sent.")
  start = time.time()
  ids = os.environ["TARGET_ID"].split(', ')
  # send greeting, if configured
  if SEND_GREETING == "true":
    for user_id in ids:
      print user_id
      sendGreeting(user_id)

  while True:
    for user_id in ids:
      sendMessage("CAT FACT: " + get_quote(), user_id)
    time.sleep(3600) # sleep for an hour

def on_close(ws):
  logging.info("\033[91m"+"Connection Closed"+"\033[0m")

def get_quote():
    quote_doc = requests.get(QUOTE_URL).content.split("\n")
    quotes = []
    for line in quote_doc:
        line = line.strip()
        if line.startswith("#") or len(line) == 0:
            # Skip any commented/empty lines
            continue
        quotes.append(line)
    return random.choice(quotes)

if __name__ == "__main__":
  r = start_rtm()
  ws = websocket.WebSocketApp(r, on_open = on_open, on_close = on_close)

  ws.run_forever()
