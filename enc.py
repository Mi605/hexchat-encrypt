#!/usr/bin/env python
# -*- coding: utf-8 -*-
# https://hexchat.readthedocs.io/en/latest/script_python.html

import hexchat
import subprocess
import os
import ConfigParser

__module_name__ = "hexchat-encrypt" 
__module_version__ = "1.0" 
__module_description__ = "hexchat symmetric encryption" 

PROCESSING = False
PASSFILE = "/home/user/pass.key"
CHANNELS = set()
DEBUG = False
MCHARSIZE = 330

""" Return channel and servername from the specified context """
def channelServer(ctxt):
	return (ctxt.get_info('channel'), ctxt.get_info('server'))

""" Return 'message' as green text """
def textPos(message): return "\x0303" + message

""" Return 'message' as red text """
def textNeg(message): return "\x0304" + message

""" Return 'message' as bold text """
def textBold(message): return "\002" + message

""" Encrypt 'plaintext' through the openssl command line client """
def encrypt(plaintext):
	process = subprocess.Popen(
		["openssl","enc","-aes-256-cbc","-e","-a","-A","-pass","file:" + PASSFILE],
		stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
	stdout,stderr = process.communicate(plaintext)      
	if process.returncode == 0: return stdout # Return as base64
	raise Exception(stderr)

""" Decrypt 'cryptogram' through the openssl command line client """
def decrypt(cryptogram):
	process = subprocess.Popen(
		["openssl","enc","-aes-256-cbc","-d","-a","-A","-pass","file:" + PASSFILE],
		stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
	stdout,stderr = process.communicate(cryptogram)
	if process.returncode == 0: return stdout
	raise Exception(stderr)

""" Invoked every time a user sends a message """
def send(word, word_eol, userdata):
	ctxt = hexchat.get_context()
	""" Only encrypt outgoing message if channel/server 
	is added to CHANNELS list """
	if channelServer(ctxt) in CHANNELS: 
		message = word_eol[0]
		try:
			""" To avoid the encrypted text gets cut off during transmission
			encrypt and send the message in chunks of MCHARSIZE character-
			length . """
			for x in range(0,len(message),MCHARSIZE): 
				""" To mark the message as encrypted, 'HEXCHATENC:' is concatenated
				to the encrypted message. """
				hexchat.command('PRIVMSG %s :%s' % 
					(ctxt.get_info('channel'), "HEXCHATENC:" 
						+ encrypt(message[x:x+MCHARSIZE])))

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
	""" If the first characters of the received message 
	is the word 'HEXCHATENC:' the text is probably encrypted """
	if message[:11] == "HEXCHATENC:":
		try:
			plaintext = decrypt(message[11:])
			PROCESSING = True
			ctxt.emit_print('Private Message to Dialog', 
				sender, textPos(plaintext))
			PROCESSING = False
			return hexchat.EAT_HEXCHAT
		except Exception as e:
			ctxt.prnt(textNeg("Could not decrypt!"))
			if DEBUG: ctxt.prnt(str(e))
			return hexchat.EAT_NONE
	return hexchat.EAT_NONE

""" Print info about encryption/debug/passfile """
def info(ctxt):
	ctxt.prnt(textBold("------------ Info ------------"))
	ctxt.prnt("* Passfile: " + PASSFILE )
	ctxt.prnt("* Debug enabled" if DEBUG else "* Debug disabled")
	if channelServer(ctxt) in CHANNELS:
		ctxt.prnt("* Encryption enabled")
	else:
		ctxt.prnt("* Encryption disabled")
	return hexchat.EAT_ALL

""" Print help summary """
def help(ctxt):
	ctxt.prnt(textBold("------------ Help ------------"))
	ctxt.prnt(textBold("/enc enable   - Enable encryption for current context"))
	ctxt.prnt(textBold("/enc disable  - Disable encryption for current context"))
	ctxt.prnt(textBold("/enc debug    - Toggle verbose error messages"))
	ctxt.prnt(textBold("/enc info     - Print status about debug/encryption"))

""" Enable outgoing encryption for current channel """
def enable(ctxt):
	CHANNELS.add(channelServer(ctxt))
	ctxt.prnt(textPos("Encryption enabled"))
	return hexchat.EAT_ALL

""" Disable outgoing encryption for current channel """
def disable(ctxt):
	if channelServer(ctxt) in CHANNELS:
		CHANNELS.remove(channelServer(ctxt))
		ctxt.prnt(textNeg("Encryption disabled"))
	return hexchat.EAT_ALL

""" Enabled/disable verbose error messages """
def debug(ctxt):
	global DEBUG
	DEBUG = DEBUG ^ 1
	ctxt.prnt("Debug enabled" 
		if DEBUG else "Debug disabled")
	return hexchat.EAT_ALL

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

""" Initialization function """
def init():
	try:
		if os.path.isfile(PASSFILE):
			hexchat.prnt(textPos(PASSFILE + " loaded! Decryption of incoming messages enabled."))
			hexchat.hook_command('', send)
			hexchat.hook_command('enc', enc,help="For help use the command /enc help")
			hexchat.hook_print('Private Message to Dialog', receive)	
		else:
			hexchat.prnt(textNeg("Could not open passfile"))
	except Exception as e:
		hexchat.prnt(textNeg(str(e)))	

init()

