#!/usr/bin/env python
# -*- coding: utf-8 -*-
# https://hexchat.readthedocs.io/en/latest/script_python.html

import hexchat
import subprocess
import os

__module_name__ = "hexchat-encrypt" 
__module_version__ = "1.0" 
__module_description__ = "hexchat symmetric encryption" 

PROCESSING = False
PASSFILE = None
CHANNELS = set()
COLORS = { 'GREEN': "\x0303", 'RED': "\x0304" }
DEBUG = False
MCHARSIZE = 330
			
def channelServer(ctx):
	return (ctx.get_info('channel'), ctx.get_info('server'))

def encrypt(plaintext):
	process = subprocess.Popen(
		["openssl","enc","-aes-256-cbc","-e","-a","-A","-pass","file:" + PASSFILE],
		stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
	stdout,stderr = process.communicate(plaintext)      
	if process.returncode == 0: return stdout
	raise Exception(stderr)

def decrypt(cryptogram):
	process = subprocess.Popen(
		["openssl","enc","-aes-256-cbc","-d","-a","-A","-pass","file:" + PASSFILE],
		stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
	stdout,stderr = process.communicate(cryptogram)
	if process.returncode == 0: return stdout
	raise Exception(stderr)
		
def send(word, word_eol, userdata):
	ctx = hexchat.get_context()
	if channelServer(ctx) in CHANNELS:
		message = word_eol[0]
		try:
			for x in range(0,len(message),MCHARSIZE): 
				hexchat.command('PRIVMSG %s :%s' % 
					(ctx.get_info('channel'), "HEXCHATENC:" 
						+ encrypt(message[x:x+MCHARSIZE])))
			hexchat.emit_print('Your Message', 
				hexchat.get_info('nick'), COLORS['GREEN'] + message)
			return hexchat.EAT_HEXCHAT
		except Exception as e:
			ctx.prnt(COLORS['RED'] + 
				"Could not encrypt!")
			if DEBUG: ctx.prnt(str(e))
			return hexchat.EAT_ALL
	return hexchat.EAT_NONE

def receive(word, word_eol, userdata):
	global PROCESSING
	if PROCESSING:
		return hexchat.EAT_NONE
	sender,message = word[0],word[1]
	ctx = hexchat.get_context()
	if message[:11] == "HEXCHATENC:":
		try:
			plaintext = decrypt(message[11:])
			PROCESSING = True
			ctx.emit_print('Private Message to Dialog', 
				sender, COLORS['GREEN'] + plaintext)
			PROCESSING = False
			return hexchat.EAT_HEXCHAT
		except Exception as e:
			ctx.prnt(COLORS['RED'] + 
				"Could not decrypt!")
			if DEBUG: ctx.prnt(str(e))
			return hexchat.EAT_NONE
	return hexchat.EAT_NONE
			
def info(ctx):
	if channelServer(ctx) in CHANNELS:
		ctx.prnt(COLORS['GREEN'] + 
		"Outgoing encryption enabled for this channel")
	else:
		ctx.prnt(COLORS['RED'] + 
		"Outgoing encryption disabled for this channel")
	return hexchat.EAT_ALL

def enable(ctx):
	CHANNELS.add(channelServer(ctx))
	ctx.prnt(COLORS['GREEN'] + "Encryption enabled")
	return hexchat.EAT_ALL

def disable(ctx):
	if channelServer(ctx) in CHANNELS:
		CHANNELS.remove(channelServer(ctx))
		ctx.prnt(COLORS['RED'] + "Encryption disabled")
	return hexchat.EAT_ALL

def debug(ctx):
	global DEBUG
	if DEBUG:
		DEBUG = False
		ctx.prnt(COLORS['GREEN'] + "Debug disabled")
	else:
		DEBUG = True
		ctx.prnt(COLORS['GREEN'] + "Debug enabled")
	return hexchat.EAT_ALL

def enc(word,word_eol,userdata):
	ctx = hexchat.get_context()
	if len(word) > 1:
		arg = word[1]
		if arg == "enable":
			enable(ctx)
		elif arg == "disable":
			disable(ctx)
		elif arg == "info":
			info(ctx)
		elif arg == "debug":
			debug(ctx)
	return hexchat.EAT_ALL

def init():
	filepath = hexchat.get_info('configdir') + "/pass.key"
	if os.path.isfile(filepath):
		global PASSFILE
		PASSFILE = filepath
		hexchat.prnt(COLORS['GREEN'] + PASSFILE + " loaded!")
		hexchat.hook_command('', send)
		hexchat.hook_command('enc',enc)
		hexchat.hook_print('Private Message to Dialog', receive)	
	else:
		hexchat.prnt(COLORS['RED'] + "No password file found! Add " + 
			filepath + " and reload script")

init()

