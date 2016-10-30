#!/usr/bin/env python
# -*- coding: utf-8 -*-
import xchat
import subprocess
import os

__module_name__ = "xchat-encrypt" 
__module_version__ = "1.0" 
__module_description__ = "XChat symmetric encryption" 

PROCESSING = False
KEYFILE = None
CHANNELS = set()
COLORS = { 'GREEN': "\x0303", 
		   'RED': "\x0304"	}
			
def channelServer(ctx):
	return (ctx.get_info('channel'), ctx.get_info('server'))

def encrypt(plaintext):
	process = subprocess.Popen(
		["openssl","enc","-aes-256-cbc","-e","-a","-A","-pass","file:"+KEYFILE],
		stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
	stdout,stderr = process.communicate(plaintext)      
	if process.returncode == 0: return stdout
	raise Exception(stderr)

def decrypt(cryptogram):
	process = subprocess.Popen(
		["openssl","enc","-aes-256-cbc","-d","-a","-A","-pass","file:"+KEYFILE],
		stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
	stdout,stderr = process.communicate(cryptogram)
	if process.returncode == 0: return stdout
	raise Exception(stderr)
		
def send(word, word_eol, userdata):
	ctx = xchat.get_context()
	if channelServer(ctx) in CHANNELS:
		message = word_eol[0]
		try:
			xchat.command('PRIVMSG %s :%s' % 
				(ctx.get_info('channel'), "ENC:" + encrypt(message)))
			xchat.emit_print('Your Message', 
				xchat.get_info('nick'), message)
			return xchat.EAT_XCHAT
		except Exception as e:
			ctx.prnt(COLORS['RED'] + "Could not encrypt!" + " " + str(e))
			return xchat.EAT_ALL
	return xchat.EAT_NONE

def receive(word, word_eol, userdata):
	global PROCESSING
	if PROCESSING:
		return xchat.EAT_NONE
	sender,message = word[0],word[1]
	ctx = xchat.get_context()
	if message[:4] == "ENC:":
		try:
			plaintext = decrypt(message[4:])
			PROCESSING = True
			ctx.emit_print('Private Message to Dialog', 
				sender, COLORS['GREEN'] + plaintext)
			PROCESSING = False
			return xchat.EAT_XCHAT
		except Exception as e:
			return xchat.EAT_NONE
	return xchat.EAT_NONE
			
def info(ctx):
	if channelServer(ctx) in CHANNELS:
		ctx.prnt(COLORS['GREEN'] + 
		"Outgoing encryption is enabled for this channel")
	else:
		ctx.prnt(COLORS['RED'] + 
		"Outgoing encryption is disabled for this channel")
	ctx.prnt("Keypath: " + 
		("No keyfile found" if KEYFILE is None else KEYFILE))
	return xchat.EAT_ALL

def enable(ctx):
	if KEYFILE is not None:
		CHANNELS.add(channelServer(ctx))
		ctx.prnt(COLORS['GREEN'] + "Encryption enabled")
	else:
		ctx.prnt(COLORS['RED'] + 
			"Encryption could not be enabled because no keyfile exists.")
	return xchat.EAT_ALL

def disable(ctx):
	if channelServer(ctx) in CHANNELS:
		CHANNELS.remove(channelServer(ctx))
		ctx.prnt(COLORS['RED'] + "Encryption disabled")
	return xchat.EAT_ALL

def enc(word,word_eol,userdata):
	ctx = xchat.get_context()
	arg = word[1]
	if arg == "enable":
		enable(ctx)
	elif arg == "disable":
		disable(ctx)
	elif arg == "info":
		info(ctx)
	return xchat.EAT_ALL

def loadKeyFile(path):
	keypath = path + "/key.bin"
	if os.path.isfile(keypath):
		global KEYFILE
		KEYFILE = keypath
		print(COLORS['GREEN'] + "Key: " + keypath + " loaded!")
	else: 
		print(COLORS['RED'] + "No keyfile found in " + path)


xchat.hook_command('', send)
xchat.hook_command('enc',enc)
xchat.hook_print('Private Message to Dialog', receive)
loadKeyFile(xchat.get_info('xchatdir'))

