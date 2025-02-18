#!/usr/bin/python
# -*- coding: utf-8 -*-
from bitcoinlib.wallets import Wallet
from bitcoinlib.mnemonic import Mnemonic
import uuid
import sys
import os

print("Checking Seeds for Used Wallers")

while True:

    id = uuid.uuid4()
    passphrase = Mnemonic().generate()
    w = Wallet.create(str(id), keys=passphrase, network='bitcoin', witness_type='p2sh-segwit')
    w.get_key()
    balance = w.balance()

    try:
        f = open("live.txt", 'a', encoding="utf8")
        print("SEED: " + str(passphrase) + " BALANCE: " + str(balance))
        if w.balance() != 0.0:
            print("SEED: " + str(passphrase) + " BALANCE: " + str(balance) + " Live")
            try:
                f.write("SEED: " + str(passphrase) + " BALANCE: " + str(balance))
            except:
                print("LIVE: " + str(passphrase))

    except:
      pass
