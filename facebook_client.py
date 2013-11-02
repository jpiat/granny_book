#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import time

import config

import os
os.environ['http_proxy']=''

import urllib2, cookielib, re, os, sys

from facepy import GraphAPI
from facepy import exceptions

#Acces token with expire time = 60days
#LONG_LIVE_ACCESS_TOKEN = 'CAAI4kaMUG1wBAPZAsSoraRJ5BoTXhRPIKfFd83CqlReSK1MYg8l7bjGqtg19ZCGTSaBWmIZBeephhnplu22GUzr3AVFfQT07yy4ZBMo1OIhlLgRl7Ey9ZAQ2VZCthZBRyjnggC4PyVEz0z2cqZCSHTcnGFgmVxpzLOouedubtrNm2zOwSNtWTUXd'
LONG_LIVE_ACCESS_TOKEN = 'CAAI4kaMUG1wBAIwCmfIXZAeZBr4DUE97OICxC9xZC6POI7epFc7a6jSBj0abLbpIah252a0bjNEuPKiCQItmwDwotPZBFZARx8jma26x9818OWmYX7rVT0wQZBH2oNsjW1E4pcnuq064UxkCM7Hz1b8IfMwh8AIFOGusDS3Lx5CZBEZA2bsqH5BBa3sdgrX2b7cZD'
#token permissions : 	email manage_notifications publish_actions read_mailbox read_stream user_friends

#Facebook app id and secret from http://developer.facebook.com/apps
APP_NAME = 'Mamiepad'
APP_ID = '625148110838620'
SECRET_KEY = '29662cafba22e554b428bef9b6a70090'


LOGIN_URL='https://login.facebook.com/login.php?login_attempt=1'


def printStatus(json_msg, f_list):
	status = []
	status.append((f_list[json_msg['source_id']]).encode('utf-8'))
	status.append((json_msg['message']).encode('utf-8'))
	return status


def printLink(json_msg, f_list):
	status = []
	status.append((f_list[json_msg['source_id']]).encode('utf-8'))
	status.append((json_msg['message']).encode('utf-8'))
	status.append((json_msg['attachment']['href']).encode('utf-8'))
	return status

def printPhoto(json_msg, f_list):
	status = []
	status.append((f_list[json_msg['source_id']]).encode('utf-8'))
        status.append((json_msg['message']).encode('utf-8'))
        status.append('')
	#print json_msg['attachment']['media'][0]['photo']['images']
	status.append((json_msg['attachment']['media'][0]['photo']['images'][0]['src']).encode('utf-8'))
	return status

def printNone(json_msg, f_list):
	status = []
        status.append((f_list[json_msg['source_id']]).encode('utf-8'))
        status.append((json_msg['message']).encode('utf-8'))
	status.append('')
	try:
		status.append((json_msg['attachment']['media'][0]['photo']['images'][0]['src']).encode('utf-8'))
	except Exception as e:
		#print e
		pass
	return status

options = {     46 : printStatus,
                        80 : printLink,
                        247 : printPhoto,
			None : printNone
        }


class FaceBookException(Exception):
	def __init__(self, value):
		self.value = value
	def __str__(self):         
		return repr(self.value)

class facebook_client:


	def __init__(self):
		self.login(config.user_id, config.user_pass)
		self.graph = GraphAPI(LONG_LIVE_ACCESS_TOKEN)
		json_output = self.graph.fql(
                'SELECT uid, name FROM user WHERE uid IN (SELECT uid1 FROM friend WHERE uid2=me())')
        	self.friendlist = {}
        	for friend in json_output['data'][:]:
                	self.friendlist[friend['uid']] = friend['name']
		self.friendlist[1011722861] = 'Jonathan Piat'


	def getLatestStreamForAll(self):
		msg = {}
		for k in self.friendlist:
			msg[self.friendlist[k]] = self.getLatestStream(k)
		return msg

	def getLatestStream(self, user):
		try:
			json_output = self.graph.fql('SELECT source_id, post_id, message, type, attachment, updated_time FROM stream WHERE source_id='+str(user)+' order by created_time')
		except exceptions.OAuthError as e :
			raise FaceBookException(str(e))
		cts = time.time()
        	ret_msg = []
		nb = 0
		for msg in  reversed(json_output['data'][:]):
                	msg_uid = msg['source_id']
                	#print msg['type']
			try:
                        	ret_msg.append(options[msg['type']](msg, self.friendlist))
                	except KeyError:
				#print 'No key for '+str(msg['type'])
                        	pass
			nb = nb + 1
			if nb > 2 :
				return ret_msg
		return ret_msg

	def login(self, user, password):
		cj = cookielib.LWPCookieJar('/root/facebook.ck')
		try:
                	cj.load()
                	print 'cookie loaded from file'
                	return
        	except cookielib.LoadError:
                	print 'cookie can not be loaded'
        	except IOError:
                	print 'cookie file does not exist'
			opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
			opener.addheaders = [('Referer', 'http://login.facebook.com/login.php'),
		    		('Content-Type', 'application/x-www-form-urlencoded'),
		    		('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.1.7) Gecko/20091221 Firefox/3.5.7 (.NET CLR 				3.5.30729)')]
        		data = "locale=en_US&non_com_login=&email="+user+"&pass="+password+"&lsd=20TOl"
        		usock = opener.open('http://www.facebook.com')
        		usock = opener.open(LOGIN_URL, data)
        		if "Logout" in usock.read():
	    			cj.save()
            			print "Logged in."
        		else:
            			print "failed login"
            			print usock.read()


if __name__ == "__main__":
	fb_client = facebook_client()
	print fb_client.getLatestStreamForAll()
	print fb_client.friendlist
