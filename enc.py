#!/usr/bin/env python
# -*- coding: utf-8 -*-
import xchat
import subprocess
import re

__module_name__ = "xchat-encrypt" 
__module_version__ = "1.0" 
__module_description__ = "XChat encryption" 

PROCESSING = False
PASSWORD = "PASS"
USERS = set()

def encrypt(plaintext):
	process = subprocess.Popen(["openssl","enc","-aes-256-cbc","-e","-a","-A","-k",PASSWORD],
		stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
	stdout,stderr = process.communicate(plaintext)
      
	if process.returncode == 0:  
		return stdout
	else:
		return stderr

def decrypt(cryptogram):
	process = subprocess.Popen(["openssl","enc","-aes-256-cbc","-d","-a","-A","-k",PASSWORD],
		stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
	stdout,stderr = process.communicate(cryptogram)

	if process.returncode == 0:  
		return stdout
	else:
		raise Exception(stderr)

def users(word, word_eol, userdata):
	print(USERS)
	xchat.EAT_XCHAT

def enable(word, word_eol, userdata):
	ctx = xchat.get_context()
	USERS.add((ctx.get_info('channel'), ctx.get_info('server')))
	xchat.EAT_XCHAT

def disable(word, word_eol, userdata):
	ctx = xchat.get_context()
	if (ctx.get_info('channel'), ctx.get_info('server')) in USERS:
		USERS.remove((ctx.get_info('channel'), ctx.get_info('server')))
	xchat.EAT_XCHAT

def encrypt_privmsg(word, word_eol, userdata):
	ctx = xchat.get_context()
	if (ctx.get_info('channel'), ctx.get_info('server')) in USERS:
		message = word_eol[0]
		xchat.command('PRIVMSG %s :%s' % (ctx.get_info('channel'), "ENC:" + encrypt(message)))
		xchat.emit_print('Your Message', xchat.get_info('nick'), message)
		return xchat.EAT_XCHAT
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
			ctx.emit_print('Private Message to Dialog', sender, "\x0303" + plaintext)
			PROCESSING = False
			return xchat.EAT_XCHAT
		except Exception as e:
			return xchat.EAT_NONE
	return xchat.EAT_NONE

xchat.hook_command('', encrypt_privmsg)
xchat.hook_command('enable_enc', enable)
xchat.hook_command('disable_enc', disable)
xchat.hook_command('users', users)
xchat.hook_print('Private Message to Dialog', decrypt_print)

