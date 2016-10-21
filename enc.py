#!/usr/bin/env python
# -*- coding: utf-8 -*-
import xchat
import subprocess

__module_name__ = "xchat-encrypt" 
__module_version__ = "1.0" 
__module_description__ = "XChat encryption" 

PROCESSING = False
PASSWORD = "PASS"
CHANNELS = set()
COLORS = {	'GREEN': "\x0303",
			'RED'  : "\x0304" 	}
			
def channelServer(ctx):
	return (ctx.get_info('channel'), ctx.get_info('server'))

def encrypt(plaintext):
	process = subprocess.Popen(["openssl","enc","-aes-256-cbc","-e","-a","-A","-k",PASSWORD],
		stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
	stdout,stderr = process.communicate(plaintext)      
	if process.returncode == 0: return stdout
	raise Exception(stderr)

def decrypt(cryptogram):
	process = subprocess.Popen(["openssl","enc","-aes-256-cbc","-d","-a","-A","-k",PASSWORD],
		stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
	stdout,stderr = process.communicate(cryptogram)
	if process.returncode == 0: return stdout
	raise Exception(stderr)
		
def encrypt_privmsg(word, word_eol, userdata):
	ctx = xchat.get_context()
	if channelServer(ctx) in CHANNELS:
		message = word_eol[0]
		try:
			xchat.command('PRIVMSG %s :%s' % (ctx.get_info('channel'), "ENC:" + encrypt(message)))
			xchat.emit_print('Your Message', xchat.get_info('nick'), message)
			return xchat.EAT_XCHAT
		except Exception as e:
			ctx.prnt(COLORS['RED'] + "Could not encrypt!")
			return xchat.EAT_ALL
	return xchat.EAT_NONE

def decrypt_print(word, word_eol, userdata):
	global PROCESSING
	if PROCESSING:
		return xchat.EAT_NONE
	sender,message = word[0],word[1]
	ctx = xchat.get_context()
	if message[:4] == "ENC:":
		try:
			plaintext = decrypt(message[4:])
			PROCESSING = True
			ctx.emit_print('Private Message to Dialog', sender, COLORS['GREEN'] + plaintext)
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
	return xchat.EAT_ALL

def enable(ctx):
	CHANNELS.add(channelServer(ctx))
	ctx.prnt(COLORS['GREEN'] + "Encryption enabled")
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
	else:
		ctx.prnt("Wrong argument")		
	return xchat.EAT_ALL

xchat.hook_command('', encrypt_privmsg)
xchat.hook_command('enc',enc)
xchat.hook_print('Private Message to Dialog', decrypt_print)

