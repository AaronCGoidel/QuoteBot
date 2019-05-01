import websocket
import json
import requests
import os
import sys
import logging
import time
import datetime as dt

logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)

TOKEN = os.environ["SLACK_API_TOKEN"]

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
  logging.info(req)

  return req['url']

def sendMessage(fact):
  user_id = os.environ["TARGET_ID"]
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

def sendGreeting():
  user_id = os.environ["TARGET_ID"]
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
  sendGreeting()
  
  filepath = "quotes.txt"
  with open(filepath) as f:
    line = f.readLine()
    count = 1
    while line:
      sendMessage(line)
      time.sleep(60) # sleep for 1 minute
      line = f.readLine()
      count += 1


def on_close(ws):
  logging.info("\033[91m"+"Connection Closed"+"\033[0m")

if __name__ == "__main__":
  r = start_rtm()
  ws = websocket.WebSocketApp(r, on_open = on_open, on_close = on_close)

  ws.run_forever()
