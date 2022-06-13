#!/usr/bin/env python
import sys
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import logging
import csv
import json
import subprocess
from subprocess import Popen
import os
import shlex
import pipes as p
import codecs
import pymongo

import bitcoinlib
from bitcoinlib.wallets import HDWallet, wallet_delete
from bitcoinlib.mnemonic import Mnemonic
import uuid

TOKEN = "

GCTM_Multisig_Wallet = ""

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

logger = logging.getLogger(__name__)

#globals
buyer = ""
seller = ""
amount = ""
ewallet = ""
fees= ""
passphrase = ""
randid = ""
p = ""
wallys = ""
escrow_channel = "-1001475038070"
d = ""

print("TEST")
#Database
myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["gctm_escrow"]

print("TEST")

#Functions
    
def start(bot, update):
  bot.send_message(chat_id=update.message.chat_id, text="Welcome to Escrow Service\n\n")
  bot.send_message(chat_id=update.message.chat_id, text="To use our services please follow the instructions\n\n")
  bot.send_message(chat_id=update.message.chat_id, text="To start the buyer must enter /buyer @yourusername\n\n")
  print("TEST")
  buyer(bot, update)

def contact(bot, update):
  bot.send_message(chat_id=escrow_channel, text="ID: "+randid+"\n\n seed:"+passphrase+"\n\n wallet:"+e+"\n\n"+update.message.from_user.username+" Requires Moderation")
  bot.send_message(chat_id=update.message.chat_id, text="admin will be in touch shortly\n\n")
  print("TEST - contact")
  
def buyer(bot, update):
  global buyer
  global amount
  if buyer != "":
    buyer = update.message.text.split(" ")[1]
    bot.send_message(chat_id=update.message.chat_id, text="Welcome "+buyer+"\n\n")
    bot.send_message(chat_id=update.message.chat_id, text="Now the seller should enter /seller @yourusername your_receiving_wallet_address\n\n")
  
def seller(bot, update):
  global seller
  global wallys
  if seller != "":
    seller = update.message.text.split(" ")[1]
    wallys = update.message.text.split(" ")[2]
    bot.send_message(chat_id=update.message.chat_id, text="Seller is "+seller+"\n Sellers wallet is "+wallys+"\n\n")
    bot.send_message(chat_id=update.message.chat_id, text="Now Generate a wallet using /generate \n\n")

def generate(bot, update):
  global randid
  global passphrase
  global w
  global key
  global ewallet
  global d
  print("test")
  mycol = mydb["gctm_deals"]
  print("Connected")
  bot.send_message(chat_id=update.message.chat_id, text="Generating new wallet, Please Wait\n\n")
  #generate randomid
  randid = uuid.uuid4() 
  #print(randid)
  
  c = str(update.message.chat_id)+str(randid)+"a"
  d = c
  
  print(str(d))

  #generate seed
  p = Mnemonic().generate()
  print(p)
  #generate wallet
  print("TEST - WALLET")
  try:
    try:
      w = HDWallet(wallet=str(d), main_key_object=str(p))
    except:
      print("ERROR")
    w = HDWallet.create(str(d), keys=str(p), network="bitcoin")
    print("WALLET CREATED")
  except:
    print("ERROR")
  key = w.get_key()
  key.address
  ewallet = key.address
  print(ewallet)
  #send seed and random id to escrow admin channel
  bot.send_message(chat_id=escrow_channel, text="ID: "+str(d)+"\nseed:"+str(p)+"\n wallet: "+str(ewallet)+"\n chatid: "+str(update.message.chat_id)+"\n buyer: "+buyer+"\n seller: "+seller)
  #send to database
  deal = {"escrow_id": d, "buyer_username": buyer, "seller_username": seller, "seller_wallet": wallys, "escrow_seed": passphrase, "escrow_wallet": ewallet, "chatid":update.message.chat_id }
  x = mycol.insert_one(deal)
  #Send Next Message
  bot.send_message(chat_id=update.message.chat_id, text="Escrow Wallet Address "+ewallet+"\n\nWallet has been Generated You may now deposit coin, your unique ID for this transaction is "+d+"\n\n type /balance to get a current balance\n\n Type /release to release the coin (only available to buyer)\n\n Type /contact for moderation")

#On Release
def release(bot, update): 
  mycol = mydb["escrow_deals"]
  id = str(d)
  try:
    bname = mycol.find_one({ "escrow_id": str(id)})
    p = bname["escrow_seed"]
    receiver_wallet = bname["seller_wallet"] 
  except:
    print("DB ERROR")
  if update.message.from_user.username in bname["buyer_username"]:
    bot.send_message(chat_id=update.message.chat_id, text="Releasing coin to seller, Please Wait")
    #calculate transaction fee for seller
    try:
      w = HDWallet(wallet=id, main_key_object=str(p))
      print("WALLET OK")
      w.scan()
    except:
      print("db fail")
    try:
      x = bitcoinlib.wallets.HDWalletTransaction(w, fee_per_kb=50)
    except:
      print("fee error")
    feesasa = x.calculate_fee()
    tfee = x.estimate_size() * feesasa
    print(tfee)
    a = w.balance()
    fee = 0.05
    fees = int(a) * fee
    rem = int(a) - fees

    feesa = int(fees) / 100000000
    feesax = format(feesa, '.8f')
    reml = float(rem) / 100000000
    remm = format(reml, '.8f')
    print("test")
    #send remainder

    try:
      t = w.send_to(str(receiver_wallet), int(rem) - tfee)
      print("Sent")
      bot.send_message(chat_id=update.message.chat_id, text=str(a)+" has been released minus our fee of "+str(feesax))
      bot.send_message(chat_id=update.message.chat_id, text=str(remm)+" has been sent to "+receiver_wallet)
      bot.send_message(chat_id=update.message.chat_id, text="Transaction ID: "+str(t))
      w.scan()
    except:
      bot.send_message(chat_id=update.message.chat_id, text="Coin Not Available or Unconfirmed, Try again shortly")
      
    try:
      x = HDWalletTransaction(w, fee_per_kb=int(31))
      t = w.send_to(GCTM_Multisig_Wallet, int(rem) - tfee)
      bot.send_message(chat_id=escrow_channel, text="Deal Complete")
      bot.send_message(chat_id=escrow_channel, text="Transaction ID: "+str(t))
      print("Sent")
    except:
      print("PROBLEM")
  else:
    bot.send_message(chat_id=update.message.chat_id, text="Only the Buyer can release funds.")

def balance(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="Getting Balance Please wait")
    id = d
    print(str(id))
    print("testing")
    try:
      mycol = mydb["escrow_deals"]
      bname = mycol.find_one({ "escrow_id": str(id)}) 
      print("TTEST")
      p = bname["escrow_seed"]
    except:
      print("ERROR")
    try:
      w = HDWallet(wallet=id, main_key_object=p)
    except:
      print("Wallet Error")
    print("NB")
    w.scan()
    global balance
    balance = int(w.balance()) / 100000000
    b2 = format(balance, '.8f')
    print(balance)
    bot.send_message(chat_id=update.message.chat_id, text="Wallet Transactions")
    bot.send_message(chat_id=update.message.chat_id, text="Balance: "+str(b2))

def error(bot, update, error):
    logger.warning('Update "%s" caused error "%s"', update, error)

def main():
    # Start the bot.
    # Create the EventHandler and pass it your bot's token.
    updater = Updater(TOKEN)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("contact", contact))
    dp.add_handler(CommandHandler("buyer", buyer))
    dp.add_handler(CommandHandler("seller", seller))
    dp.add_handler(CommandHandler("release", release))
    dp.add_handler(CommandHandler("balance", balance))
    dp.add_handler(CommandHandler("generate", generate))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()

