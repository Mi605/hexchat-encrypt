#!/usr/bin/env python
# -*- coding: utf-8 -*-

# The MIT License (MIT)
# 
# Copyright (c) [2016] [Robert Kvant]
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE

# HexChat Python Interface Documentation
# https://hexchat.readthedocs.io/en/latest/script_python.html

import hexchat
import subprocess
import os

__module_name__ = "hexchat-encrypt" 
__module_version__ = "1.0.0"
__module_description__ = "hexchat symmetric encryption" 

PROCESSING = False
PASSFILE = "/home/user/pass.key" # Path to passwordfile 
DIALOGS = set()
DEBUG = False
MCHARSIZE = 330

""" Encrypt 'plaintext' through the openssl command line client """
def encrypt(plaintext):
	process = subprocess.Popen(
		["openssl","enc","-aes-256-cbc","-iter","5000","-e","-salt","-a","-A","-pass","file:" + PASSFILE],
		stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
	stdout,stderr = process.communicate(plaintext)      
	if process.returncode == 0: return stdout # Return as base64
	raise Exception(stderr)

""" Decrypt 'cryptogram' through the openssl command line client """
def decrypt(cryptogram):
	process = subprocess.Popen(
		["openssl","enc","-aes-256-cbc","-iter","5000","-d","-salt","-a","-A","-pass","file:" + PASSFILE],
		stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
	stdout,stderr = process.communicate(cryptogram)
	if process.returncode == 0: return stdout
	raise Exception(stderr)

""" Invoked every time a user sends a message """
def send(word, word_eol, userdata):
	ctxt = hexchat.get_context()
	""" Only encrypt outgoing message if channel/server 
	is added to DIALOGS list """
	if channelServer(ctxt) in DIALOGS: 
		try:
			message = word_eol[0]
			""" To avoid the encrypted text gets cut off during transmission
			encrypt and send the message in chunks of MCHARSIZE character-
			length . """
			for x in range(0,len(message),MCHARSIZE): 
				""" To mark the message as encrypted, 'HEXCHATENC:' is 
				concatenated to the encrypted message. """
				hexchat.command('PRIVMSG %s :%s' % 
					(ctxt.get_info('channel'), "HEXCHATENC:" 
						+ encrypt(message[x:x+MCHARSIZE])))
			""" Message sent, print to dialog window"""
			hexchat.emit_print('Your Message', 
				hexchat.get_info('nick'), textPos(message))
			return hexchat.EAT_HEXCHAT
		except Exception as e:
			ctxt.prnt(textNeg("Could not encrypt!"))
			if DEBUG: ctxt.prnt(str(e))
			return hexchat.EAT_ALL
	return hexchat.EAT_NONE

""" Invoked every time a message is received in a private dialog """
def receive(word, word_eol, userdata):
	global PROCESSING
	if PROCESSING:
		return hexchat.EAT_NONE
	sender,message = word[0],word[1]
	ctxt = hexchat.get_context()
	""" If the first 11 characters of the received message 
	is the word 'HEXCHATENC:' the text is probably encrypted """
	if message[:11] == "HEXCHATENC:":
		try:
			plaintext = decrypt(message[11:])
			""" If sender not in DIALOGS -> enable outgoing 
			encryption for this context """
			if channelServer(ctxt) not in DIALOGS:
				enable(ctxt)

			PROCESSING = True
			""" Message decrypted, print to dialog window"""
			ctxt.emit_print('Private Message to Dialog', 
				sender, textPos(plaintext))
			PROCESSING = False
			return hexchat.EAT_HEXCHAT
		except Exception as e:
			ctxt.prnt(textNeg("Could not decrypt!"))
			if DEBUG: ctxt.prnt(str(e))
	return hexchat.EAT_NONE

""" Enable outgoing encryption on current channel """
def enable(ctxt):
	if isDialog(ctxt):
		DIALOGS.add(channelServer(ctxt))
		ctxt.prnt(textPos("Encryption enabled"))
	else:
		ctxt.prnt(textNeg("Encryption can only be enabled" + 
			" on private dialog windows"))
	return hexchat.EAT_ALL

""" Disable outgoing encryption on current channel """
def disable(ctxt):
	if channelServer(ctxt) in DIALOGS:
		DIALOGS.remove(channelServer(ctxt))
	ctxt.prnt(textNeg("Encryption disabled"))
	return hexchat.EAT_ALL

""" Enable/disable verbose error messages """
def debug(ctxt):
	global DEBUG
	DEBUG ^= 1
	ctxt.prnt("Debug enabled" if DEBUG
		else "Debug disabled")
	return hexchat.EAT_ALL

""" Return channel and servername from the specified context """
def channelServer(ctxt):
	return (ctxt.get_info('channel'), ctxt.get_info('server'))

""" Returns true if current context is a dialog window """
def isDialog(ctxt):
	return [x.type for x in ctxt.get_list('channels') 
		if x.channel == ctxt.get_info('channel')][0] == 3

""" Return 'message' as green text """
def textPos(message): 
	return "\x0303" + message

""" Return 'message' as red text """
def textNeg(message): 
	return "\x0304" + message

""" Return 'message' as bold text """
def textBold(message): 
	return "\002"  + message

""" Handles all /enc command arguments"""
def enc(word,word_eol,userdata):
	ctxt = hexchat.get_context()
	try:
		arg = word[1]
		if arg == "enable":
			enable(ctxt)
		elif arg == "disable":
			disable(ctxt)
		elif arg == "info":
			info(ctxt)
		elif arg == "debug":
			debug(ctxt)
		else:
			raise Exception
	except Exception:
		help(ctxt)
	return hexchat.EAT_ALL

""" Initialization"""
def init():
	try:
		if os.path.isfile(PASSFILE):
			hexchat.prnt(textPos(PASSFILE + " loaded!"))
			hexchat.hook_command('', send)
			hexchat.hook_command('enc', enc, help="For help use the command /enc")
			hexchat.hook_print('Private Message to Dialog', receive)	
		else:
			hexchat.prnt(textNeg("Could not open passfile"))
	except Exception as e:
		hexchat.prnt(textNeg(str(e)))	

""" Print info about encryption/debug/passfile """
def info(ctxt):
	ctxt.prnt(textBold("------------------ Info ------------------"))
	ctxt.prnt("* Passfile: " + PASSFILE )
	ctxt.prnt("* Debug enabled" if DEBUG else "* Debug disabled")
	ctxt.prnt("* Encryption enabled" if channelServer(ctxt) in 
		DIALOGS else "* Encryption disabled")
	return hexchat.EAT_ALL

""" Print help summary """
def help(ctxt):
	ctxt.prnt(textBold("------------------ Help ------------------"))
	ctxt.prnt("/enc enable   - Encrypt outgoing messages on current dialog window")
	ctxt.prnt("/enc disable  - Disable encryption of outgoing messages on current dialog window")
	ctxt.prnt("/enc info     - Print status about debug/encryption")
	return hexchat.EAT_ALL

init()

