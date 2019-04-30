import websocket
import json
import requests
import urllib
import os
import sys
import logging
import time

logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)

try:
  TOKEN = os.environ["SLACK_API_TOKEN"]
except:
  TOKEN = 'TOKEN NOT FOUND'

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

def sendMessage():
  logging.info("Sent Message!")
  return True

def sendGreeting():
  logging.info("Greeting Sent")
  return True

def on_open(ws):
  logging.info("\033[32m"+"Connection Opened"+"\033[0m" + ", messages will be sent every hour")
  start = time.time()
  while True:
    sendMessage()
    time.sleep(60 - ((time.time() - start) % 60))

def on_close(ws):
  logging.info("\033[91m"+"Connection Closed"+"\033[0m")

if __name__ == "__main__":
  r = start_rtm()
  ws = websocket.WebSocketApp(r, on_open = on_open, on_close = on_close)

  ws.run_forever()