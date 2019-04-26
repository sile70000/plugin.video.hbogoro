# -*- coding: utf-8 -*-

import re
import sys
import os
import urllib
import urllib2
import requests
import json
import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon
import xbmcvfs
import base64
import time
import random
import inputstreamhelper
import ssl
import uuid

__addon_id__= 'plugin.video.hbogoro'
__Addon = xbmcaddon.Addon(__addon_id__)
__settings__ = xbmcaddon.Addon(id='plugin.video.hbogoro')

UA = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.79 Safari/537.36'
MUA = 'Dalvik/2.1.0 (Linux; U; Android 8.0.0; Nexus 5X Build/OPP3.170518.006)'

se = __settings__.getSetting('se')
language = __settings__.getSetting('language')
HBOlanguage = __settings__.getSetting('HBOlanguage')

if language == '0':
	lang = 'English'
	Code = 'ENG'
	srtsubs_path = xbmc.translatePath('special://temp/hbogo.English.Forced.srt')
elif language == '1':
	lang = 'Romanian'
	Code = 'RON'
	srtsubs_path = xbmc.translatePath('special://temp/hbogo.Romanian.Forced.srt')
elif language == '2':
	lang = 'English'
	Code = 'ENG'
	srtsubs_path = xbmc.translatePath('special://temp/hbogo.English.Forced.srt')
	
if HBOlanguage == '0':
	HBOlang = 'English'
	HBOCode = 'ENG'
	FavString='Favorites'
	SearchString='Search for movies, episodes ...'
	EpisodeString=' Episode '
elif HBOlanguage == '1':
	HBOlang = 'Romanian'
	HBOCode = 'RON'
	FavString='Favorite'
	SearchString='Căutare filme, seriale ...'
	EpisodeString=' Episodul '
elif HBOlanguage == '2':
	HBOlang = 'English'
	HBOCode = 'ENG'
	FavString='Favorites'
	SearchString='Search for movies, episodes ...'
	EpisodeString=' Episode '

md = xbmc.translatePath(__Addon.getAddonInfo('path') + "/resources/media/")
search_string = urllib.unquote_plus(__settings__.getSetting('lastsearch'))

operator = __settings__.getSetting('operator')
op_ids = [
'00000000-0000-0000-0000-000000000000', # Anonymous NoAuthenticated
'defb1446-0d52-454c-8c86-e03715f723a8', # AKTA
'381ba411-3927-4616-9c6a-b247d3ce55e8', # Canal S
'4949006b-8112-4c09-87ad-18d6f7bfee02', # HBO GO Vip/Club Romania
'0539b12f-670e-49ff-9b09-9cef382e4dae', # INES
'078a922e-df7c-4f34-a8de-842dea7f4342', # INTERSAT
'cb71c5a8-9f21-427a-a37e-f08abf9605be', # Metropolitan
'959cf6b2-34b1-426d-9d51-adf04c0802b0', # MITnet
'cf66ff47-0568-485f-902d-0accc1547ced', # NextGen Communications
'754751b7-1406-416e-b4bd-cb6566656de2', # Orange Romania
'c243a2f3-d54e-4365-85ad-849b6908d53e', # RCS RDS
'972706fe-094c-4ea5-ae98-e8c5d907f6a2', # Telekom Romania
'6baa4a6e-d707-42b2-9a79-8b475c125d86', # Telekom Romania Business
'd68c2237-1f3f-457e-a708-e8e200173b8d', # TV SAT 2002
'41a660dc-ee15-4125-8e92-cdb8c2602c5d', # UPC Romania
'92e30168-4ca6-4512-967d-b79e584a22b6', # Vodafone
'6826b525-04dc-4bb9-ada5-0a8e80a9f55a', # Vodafone Romania 4GTV+
'da5a4764-a001-4dac-8e52-59d0ae531a62', # Voucher HBOGO
													
												  
																			 
													  
																 
																 
]
op_id = op_ids[int(operator)];

individualization = ""
goToken = ""
customerId = ""
GOcustomerId = ""
sessionId = '00000000-0000-0000-0000-000000000000'
FavoritesGroupId = ""

loggedin_headers = {
	'User-Agent': UA,
	'Accept': '*/*',
	'Accept-Language': 'en-US,en;q=0.5',
	'Referer': 'https://www.hbogo.ro/',
	'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
	'Origin': 'https://www.hbogo.ro',
	'X-Requested-With': 'XMLHttpRequest',
	'GO-Language': 'RON',
	'GO-requiredPlatform': 'CHBR',
	'GO-Token': '',
	'GO-SessionId': '',
	'GO-swVersion': '4.8.0',
	'GO-CustomerId': '',
	'Connection': 'keep-alive',
	'Accept-Encoding': ''
}

# individualization es customerId storing
def storeIndiv(indiv, custid):
	global individualization
	global customerId

	individualization = __settings__.getSetting('individualization')
	if individualization == "":
		__settings__.setSetting('individualization', indiv)
		individualization = indiv

	customerId = __settings__.getSetting('customerId')
	if customerId == "":
		__settings__.setSetting('customerId', custid)
		customerId = custid

# FavoritesGroupId storing
def storeFavgroup(favgroupid):
	global FavoritesGroupId

	FavoritesGroupId = __settings__.getSetting('FavoritesGroupId')
	if FavoritesGroupId == "":
		__settings__.setSetting('FavoritesGroupId', favgroupid)
		FavoritesGroupId = favgroupid

# Register
def SILENTREGISTER():
	global goToken
	global individualization
	global customerId
	global sessionId

	req = urllib2.Request('https://ro.hbogo.eu/services/settings/silentregister.aspx', None, loggedin_headers)

	opener = urllib2.build_opener()
	f = opener.open(req)
	jsonrsp = json.loads(f.read())

	if jsonrsp['Data']['ErrorMessage']:
		xbmcgui.Dialog().ok('Error', jsonrsp['Data']['ErrorMessage'])

	indiv = jsonrsp['Data']['Customer']['CurrentDevice']['Individualization']
	custid = jsonrsp['Data']['Customer']['CurrentDevice']['Id'];
	storeIndiv(indiv, custid)

	sessionId= jsonrsp['Data']['SessionId']
	return jsonrsp

# Favorite list
def GETFAVORITEGROUP():
	global FavoritesGroupId

	req = urllib2.Request('https://roapi.hbogo.eu/v8/Settings/json/'+HBOCode+'/COMP', None, loggedin_headers)

	opener = urllib2.build_opener()
	f = opener.open(req)
	jsonrsp = json.loads(f.read())

	favgroupId = jsonrsp['FavoritesGroupId']
	storeFavgroup(favgroupId)

# Login
def LOGIN():
	global sessionId
	global goToken
	global customerId
	global GOcustomerId
	global individualization
	global loggedin_headers
	global FavoritesGroupId

	operator = __settings__.getSetting('operator')
	username = __settings__.getSetting('username')
	password = __settings__.getSetting('password')
	customerId = __settings__.getSetting('customerId')
	individualization = __settings__.getSetting('individualization')
	FavoritesGroupId = __settings__.getSetting('FavoritesGroupId')

	if (individualization == "" or customerId == ""):
		jsonrsp = SILENTREGISTER()

	if (FavoritesGroupId == ""):
		GETFAVORITEGROUP()

	if (username=="" or password==""):
		xbmcgui.Dialog().ok('Error', 'Please enter the login details in the plugin settings!')
		xbmcaddon.Addon(id='plugin.video.hbogoro').openSettings("Account")
		xbmc.executebuiltin("Container.Refresh")
		LOGIN()

	headers = {
		'Origin': 'https://gateway.hbogo.eu',
		'Accept-Encoding': 'gzip, deflate, br',
		'Accept-Language': 'ro-RO,en-US;q=0.9,en;q=0.8',
		'User-Agent': UA,
		'GO-Token': '',
		'Accept': 'application/json',
		'GO-SessionId': '',
		'Referer': 'https://gateway.hbogo.eu/signin/form',
		'Connection': 'keep-alive',
		'GO-CustomerId': '00000000-0000-0000-0000-000000000000',
		'Content-Type': 'application/json',
	}

    # todo: instead of gateway you can get back to bulgar's version, but at the moment it's okay the links have been removed from the site
											
	#if operator == '1':
	#	url = 'https://api.ugw.hbogo.eu/v3.0/Authentication/ROU/JSON/RON/COMP'
	#else:
	#	url = 'https://rogwapi.hbogo.eu/v2.1/Authentication/json/RON/COMP'
	
	url = 'https://rogwapi.hbogo.eu/v2.1/Authentication/json/RON/COMP'
	data_obj = {
		"Action": "L",
		"AppLanguage": None,
		"ActivationCode": None,
		"AllowedContents": [],
		"AudioLanguage": None,
		"AutoPlayNext": False,
		"BirthYear": 1,
		"CurrentDevice": {
			"AppLanguage":"",
			"AutoPlayNext": False,
			"Brand": "Chromium",
			"CreatedDate": "",
			"DeletedDate": "",
			"Id": "00000000-0000-0000-0000-000000000000",
			"Individualization": individualization,
			"IsDeleted": False,
			"LastUsed": "",
			"Modell": "62",
			"Name": "",
			"OSName": "Ubuntu",
			"OSVersion": "undefined",
			"Platform": "COMP",
			"SWVersion": "2.4.2.4025.240",
			"SubtitleSize": ""
		},
		"CustomerCode": "",
		"DebugMode": False,
		"DefaultSubtitleLanguage": None,
		"EmailAddress": username,
		"FirstName": "",
		"Gender": 0,
		"Id": "00000000-0000-0000-0000-000000000000",
		"IsAnonymus": True,
		"IsPromo": False,
		"Language": HBOCode,
		"LastName": "",
		"Nick": "",
		"NotificationChanges": 0,
		"OperatorId": op_id,
		"OperatorName": "",
		"OperatorToken": "",
		"ParentalControl": {
			"Active": False,
			"Password": "",
			"Rating": 0,
			"ReferenceId": "00000000-0000-0000-0000-000000000000"
		},
		"Password": password,
		"PromoCode": "",
		"ReferenceId": "00000000-0000-0000-0000-000000000000",
		"SecondaryEmailAddress": "",
		"SecondarySpecificData": None,
		"ServiceCode": "",
		"SubscribeForNewsletter": False,
		"SubscState": None,
		"SubtitleSize": "",
		"TVPinCode": "",
		"ZipCode": ""
	}

	data = json.dumps(data_obj)				
	r = requests.post(url, headers=headers, data=data)



	jsonrspl = json.loads(r.text)

	try:
		if jsonrspl['ErrorMessage']:
			xbmcgui.Dialog().ok('Login Error!', jsonrspl['ErrorMessage'])
	except:
		pass

	customerId = jsonrspl['Customer']['CurrentDevice']['Id']
	individualization = jsonrspl['Customer']['CurrentDevice']['Individualization']

	sessionId = jsonrspl['SessionId']
	if sessionId == '00000000-0000-0000-0000-000000000000':
		xbmcgui.Dialog().ok('Login error!','Check log details!')
		xbmcaddon.Addon(id='plugin.video.hbogoro').openSettings("Account")
		xbmc.executebuiltin("Action(Back)")
	else:
		goToken = jsonrspl['Token']
		GOcustomerId = jsonrspl['Customer']['Id']

		loggedin_headers['GO-SessionId'] = str(sessionId)
		loggedin_headers['GO-Token'] = str(goToken)
		loggedin_headers['GO-CustomerId'] = str(GOcustomerId)

# Categories
def CATEGORIES():
	global FavoritesGroupId

	addDir(SearchString,'search','',4,md+'DefaultAddonsSearch.png')

	if (FavoritesGroupId == ""):
		GETFAVORITEGROUP()

	if (FavoritesGroupId != ""):
		addDir(FavString,'https://roapi.hbogo.eu/v8/CustomerGroup/json/'+HBOCode+'/COMP/'+FavoritesGroupId+'/-/-/-/1000/-/-/false','',1,md+'FavoritesFolder.png')

	req = urllib2.Request('http://roapi.hbogo.eu/v8/Groups/json/'+HBOCode+'/ANMO/0/True', None, loggedin_headers)
	opener = urllib2.build_opener()
	f = opener.open(req)
	#xbmc.log('mesaj_sile_link '+'http://roapi.hbogo.eu/v8/Groups/json/'+HBOCode+'/ANMO/0/True', xbmc.LOGNOTICE)
	jsonrsp = json.loads(f.read())

	try:
		if jsonrsp['ErrorMessage']:
			xbmcgui.Dialog().ok('Error', jsonrsp['ErrorMessage'])
	except:
		pass
	#xbmc.log('mesaj_sile_categorii '+str(jsonrsp), xbmc.LOGNOTICE)
	for cat in range(1, 3):
		addDir(jsonrsp['Items'][cat]['Name'].encode('utf-8', 'ignore'),jsonrsp['Items'][cat]['ObjectUrl'],'',1,md+'DefaultFolder.png')
	for cat in range(0, 1):
		req = urllib2.Request(jsonrsp['Items'][cat]['ObjectUrl'], None, loggedin_headers)
		opener = urllib2.build_opener()
		f = opener.open(req)
		jsonrsp2 = json.loads(f.read())

		try:
			if jsonrsp2['ErrorMessage']:
				xbmcgui.Dialog().ok('Error', jsonrsp2['ErrorMessage'])
		except:
			pass
		#xbmc.log('mesaj_sile_lista2 '+str(jsonrsp2), xbmc.LOGNOTICE)
		# If there is a subcategory / genres
		if len(jsonrsp2['Container']) > 1:
			for Container in range(0, len(jsonrsp2['Container'])):
				addDir(jsonrsp2['Container'][Container]['Name'].encode('utf-8', 'ignore'),jsonrsp2['Container'][Container]['ObjectUrl'],'',1,md+'DefaultFolder.png')
	
		#addDir(jsonrsp['Items'][3]['Name'].encode('utf-8', 'ignore'),'https://roapi.hbogo.eu/v8/Group/json/RON/COMP/960fdc80-adc1-4e39-8da0-073a777414d8/0/0/0/0/0/0/True','',1,md+'DefaultFolder.png')
# List
def LIST(url):
	global sessionId
	global loggedin_headers

	if sessionId == '00000000-0000-0000-0000-000000000000':
		LOGIN()

	req = urllib2.Request(url, None, loggedin_headers)
	opener = urllib2.build_opener()
	f = opener.open(req)
	jsonrsp = json.loads(f.read())

	try:
		if jsonrsp['ErrorMessage']:
			xbmcgui.Dialog().ok('Error', jsonrsp['ErrorMessage'])
	except:
		pass
	# If there is a subcategory / genres
	if len(jsonrsp['Container']) > 1:
		for Container in range(0, len(jsonrsp['Container'])):
			addDir(jsonrsp['Container'][Container]['Name'].encode('utf-8', 'ignore'),jsonrsp['Container'][Container]['ObjectUrl'],'',1,md+'DefaultFolder.png')
	else:
		xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_UNSORTED)
		xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_DATE)
		xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_TITLE)
		#If there are no subcategories / species
		for titles in range(0, len(jsonrsp['Container'][0]['Contents']['Items'])):

			allowplay = jsonrsp['Container'][0]['Contents']['Items'][titles].get( 'AllowPlay', None )
			if allowplay is None:
				allowplay = False

			if jsonrsp['Container'][0]['Contents']['Items'][titles]['ContentType'] == 1: #1=MOVIE/EXTRAS, 2=SERIES(serial), 3=SERIES(episode)
				#Movies
				xbmcplugin.setContent(int(sys.argv[1]), 'movie')
				plot = jsonrsp['Container'][0]['Contents']['Items'][titles].get( 'Description', None )
				if plot is None:
					plot = jsonrsp['Container'][0]['Contents']['Items'][titles].get( 'Abstract', None )
				if plot is None:
					plot = ''
				plot.encode('utf-8', 'ignore')
				firstGenre = jsonrsp['Container'][0]['Contents']['Items'][titles]['Genre']
				secondGenre = jsonrsp['Container'][0]['Contents']['Items'][titles]['SecondaryGenre']
				genre = [firstGenre.capitalize(), secondGenre.capitalize()]
				date = jsonrsp['Container'][0]['Contents']['Items'][titles]['AvailabilityFrom']
				addLink(jsonrsp['Container'][0]['Contents']['Items'][titles]['ObjectUrl'],plot,jsonrsp['Container'][0]['Contents']['Items'][titles]['AgeRating'],jsonrsp['Container'][0]['Contents']['Items'][titles]['ImdbRate'],jsonrsp['Container'][0]['Contents']['Items'][titles]['BackgroundUrl'],[jsonrsp['Container'][0]['Contents']['Items'][titles]['Cast'].split(', ')][0],jsonrsp['Container'][0]['Contents']['Items'][titles]['Director'],jsonrsp['Container'][0]['Contents']['Items'][titles]['Writer'],jsonrsp['Container'][0]['Contents']['Items'][titles]['Duration'],genre,jsonrsp['Container'][0]['Contents']['Items'][titles]['Name'].encode('utf-8', 'ignore'),jsonrsp['Container'][0]['Contents']['Items'][titles]['OriginalName'],jsonrsp['Container'][0]['Contents']['Items'][titles]['ProductionYear'],5,date,allowplay)
				#xbmc.log("GO: FILMI: DUMP: " + jsonrsp['Container'][0]['Contents']['Items'][titles]['ObjectUrl'], xbmc.LOGNOTICE)
				
			elif jsonrsp['Container'][0]['Contents']['Items'][titles]['ContentType'] == 3:
				#Episodes
				xbmcplugin.setContent(int(sys.argv[1]), 'episode')
				plot = jsonrsp['Container'][0]['Contents']['Items'][titles].get( 'Description', None )
				if plot is None:
					plot = ''
				plot.encode('utf-8', 'ignore')
				firstGenre = jsonrsp['Container'][0]['Contents']['Items'][titles]['Genre']
				secondGenre = jsonrsp['Container'][0]['Contents']['Items'][titles]['SecondaryGenre']
				genre = [firstGenre.capitalize(), secondGenre.capitalize()]
				date = jsonrsp['Container'][0]['Contents']['Items'][titles]['AvailabilityFrom']
				addLink(jsonrsp['Container'][0]['Contents']['Items'][titles]['ObjectUrl'],plot,jsonrsp['Container'][0]['Contents']['Items'][titles]['AgeRating'],jsonrsp['Container'][0]['Contents']['Items'][titles]['ImdbRate'],jsonrsp['Container'][0]['Contents']['Items'][titles]['BackgroundUrl'],[jsonrsp['Container'][0]['Contents']['Items'][titles]['Cast'].split(', ')][0],jsonrsp['Container'][0]['Contents']['Items'][titles]['Director'],jsonrsp['Container'][0]['Contents']['Items'][titles]['Writer'],jsonrsp['Container'][0]['Contents']['Items'][titles]['Duration'],genre,jsonrsp['Container'][0]['Contents']['Items'][titles]['SeriesName'].encode('utf-8', 'ignore')+' S'+str(jsonrsp['Container'][0]['Contents']['Items'][titles]['SeasonIndex'])+EpisodeString+str(jsonrsp['Container'][0]['Contents']['Items'][titles]['Index']),jsonrsp['Container'][0]['Contents']['Items'][titles]['OriginalName'],jsonrsp['Container'][0]['Contents']['Items'][titles]['ProductionYear'],5,date,allowplay)
			else:
				#Series
				xbmcplugin.setContent(int(sys.argv[1]), 'season')
				plot = jsonrsp['Container'][0]['Contents']['Items'][titles].get( 'Description', None )
				if plot is None:
					plot = jsonrsp['Container'][0]['Contents']['Items'][titles].get( 'Abstract', None )
				if plot is None:
					plot = ''
				plot.encode('utf-8', 'ignore')
				addDir(jsonrsp['Container'][0]['Contents']['Items'][titles]['Name'].encode('utf-8', 'ignore'),jsonrsp['Container'][0]['Contents']['Items'][titles]['ObjectUrl'],plot,2,jsonrsp['Container'][0]['Contents']['Items'][titles]['BackgroundUrl'])


# Season
def SEASON(url):
	req = urllib2.Request(url, None, loggedin_headers)
	opener = urllib2.build_opener()
	f = opener.open(req)
	jsonrsp = json.loads(f.read())

	try:
		if jsonrsp['ErrorMessage']:
			xbmcgui.Dialog().ok('Error', jsonrsp['ErrorMessage'])
	except:
		pass
	for season in range(0, len(jsonrsp['Parent']['ChildContents']['Items'])):
		plot = jsonrsp['Parent']['ChildContents']['Items'][season].get( 'Description', None )
		if plot is None:
			plot = jsonrsp['Parent']['ChildContents']['Items'][season].get( 'Abstract', None )
		if plot is None:
			plot = ''
		plot.encode('utf-8', 'ignore')
		addDir(jsonrsp['Parent']['ChildContents']['Items'][season]['Name'].encode('utf-8', 'ignore'),jsonrsp['Parent']['ChildContents']['Items'][season]['ObjectUrl'],plot,3,jsonrsp['Parent']['ChildContents']['Items'][season]['BackgroundUrl'])

# Episode
def EPISODE(url):
	xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_UNSORTED)
	xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_DATE)
	xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_TITLE)
	xbmcplugin.setContent(int(sys.argv[1]), 'episode')
	req = urllib2.Request(url, None, loggedin_headers)
	opener = urllib2.build_opener()
	f = opener.open(req)
	jsonrsp = json.loads(f.read())

	try:
		if jsonrsp['ErrorMessage']:
			xbmcgui.Dialog().ok('Error', jsonrsp['ErrorMessage'])
	except:
		pass

	for episode in range(0, len(jsonrsp['ChildContents']['Items'])):
		# addLink(ou,plot,ar,imdb,bu,cast,director,writer,duration,genre,name,on,py,mode)
		plot = jsonrsp['ChildContents']['Items'][episode].get( 'Description', None )
		if plot is None:
			plot = ''
		plot.encode('utf-8', 'ignore')
		firstGenre = jsonrsp['Genre']
		secondGenre = jsonrsp['SecondaryGenre']
		genre = [firstGenre.capitalize(), secondGenre.capitalize()]
		date = jsonrsp['AvailabilityFrom']
		allowplay = jsonrsp['ChildContents']['Items'][episode].get( 'AllowPlay', None )
		if allowplay is None:
			allowplay = False
		addLink(jsonrsp['ChildContents']['Items'][episode]['ObjectUrl'],plot,jsonrsp['ChildContents']['Items'][episode]['AgeRating'],jsonrsp['ChildContents']['Items'][episode]['ImdbRate'],jsonrsp['ChildContents']['Items'][episode]['BackgroundUrl'],[jsonrsp['ChildContents']['Items'][episode]['Cast'].split(', ')][0],jsonrsp['ChildContents']['Items'][episode]['Director'],jsonrsp['ChildContents']['Items'][episode]['Writer'],jsonrsp['ChildContents']['Items'][episode]['Duration'],genre,jsonrsp['ChildContents']['Items'][episode]['SeriesName'].encode('utf-8', 'ignore')+' S'+str(jsonrsp['ChildContents']['Items'][episode]['SeasonIndex'])+' '+jsonrsp['ChildContents']['Items'][episode]['Name'].encode('utf-8', 'ignore'),jsonrsp['ChildContents']['Items'][episode]['OriginalName'],jsonrsp['ChildContents']['Items'][episode]['ProductionYear'],5,date,allowplay)
		
# Play 
def PLAY(url):
	global goToken
	global individualization
	global customerId
	global GOcustomerId
	global sessionId
	global loggedin_headers

	if sessionId == '00000000-0000-0000-0000-000000000000':
		LOGIN()

	if se=='true':
		try:
			#print 'CID '+cid
			#http://roapi.hbogo.eu/player50.svc/Content/json/RON/COMP/
			#http://roapi.hbogo.eu/player50.svc/Content/json/RON/APPLE/
			#http://roapi.hbogo.eu/player50.svc/Content/json/RON/SONY/
			req = urllib2.Request('http://roapi.hbogo.eu/v8/Content/json/RON/ANMO/'+cid, None, loggedin_headers)
			req.add_header('User-Agent', MUA)
			opener = urllib2.build_opener()
			f = opener.open(req)
			jsonrsps = json.loads(f.read())
			#print jsonrsps

			try:
				if jsonrsps['Subtitles'][0]['Code']==Code:
					slink = jsonrsps['Subtitles'][0]['Url']
				elif jsonrsps['Subtitles'][1]['Code']==Code:
					slink = jsonrsps['Subtitles'][1]['Url']
				req = urllib2.Request(slink, None, loggedin_headers)
				response = urllib2.urlopen(req)
				data=response.read()
				response.close()

				subs = re.compile('<p[^>]+begin="([^"]+)\D(\d+)"[^>]+end="([^"]+)\D(\d+)"[^>]*>([\w\W]+?)</p>').findall(data)
				row = 0
				buffer = ''
				for sub in subs:
					row = row + 1
					buffer += str(row) +'\n'
					buffer += "%s,%03d" % (sub[0], int(sub[1])) + ' --> ' + "%s,%03d" % (sub[2], int(sub[3])) + '\n'
					buffer += urllib.unquote_plus(sub[4]).replace('<br/>','\n').replace('<br />','\n').replace("\r\n", "").replace("&lt;", "<").replace("&gt;", ">").replace("\n    ","").strip()
					buffer += '\n\n'
					sub = 'true'
					with open(srtsubs_path, "w") as subfile:
						subfile.write(buffer)

				if sub != 'true':
					raise Exception()

			except:
				sub = 'false'
		except:
			sub = 'false'


	purchase_payload = '<Purchase xmlns="go:v8:interop" xmlns:i="http://www.w3.org/2001/XMLSchema-instance"><AllowHighResolution>true</AllowHighResolution><ContentId>'+cid+'</ContentId><CustomerId>'+GOcustomerId+'</CustomerId><Individualization>'+individualization+'</Individualization><OperatorId>'+op_id+'</OperatorId><IsFree>false</IsFree><RequiredPlatform>COMP</RequiredPlatform><UseInteractivity>false</UseInteractivity></Purchase>'

	purchase_headers = {
		'Accept': 'application/json, text/javascript, */*; q=0.01',
		'Accept-Encoding': '',
		'Accept-Language': 'en-US,en;q=0.8',
		'Connection': 'keep-alive',
		'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
		'GO-CustomerId': str(GOcustomerId),
		'GO-requiredPlatform': 'CHBR',
		'GO-SessionId': str(sessionId),
		'GO-swVersion': '4.7.4',
		'GO-Token': str(goToken),
		'Host': 'roapi.hbogo.eu',
		'Referer': 'https://hbogo.ro/',
		'Origin': 'https://www.hbogo.ro',
		'User-Agent': UA
		}

	req = urllib2.Request('https://roapi.hbogo.eu/v8/Purchase/Json/RON/COMP', purchase_payload, purchase_headers)
	opener = urllib2.build_opener()
	f = opener.open(req)
	jsonrspp = json.loads(f.read())
	print jsonrspp

	try:
		if jsonrspp['ErrorMessage']:
			xbmcgui.Dialog().ok('Error',jsonrspp['ErrorMessage'])
	except:
		pass

	MediaUrl = jsonrspp['Purchase']['MediaUrl'] + "/Manifest"
	PlayerSessionId = jsonrspp['Purchase']['PlayerSessionId']
	x_dt_auth_token = jsonrspp['Purchase']['AuthToken']
	dt_custom_data = base64.b64encode("{\"userId\":\"" + GOcustomerId + "\",\"sessionId\":\"" + PlayerSessionId + "\",\"merchant\":\"hboeurope\"}")


	li = xbmcgui.ListItem(iconImage=thumbnail, thumbnailImage=thumbnail, path=MediaUrl)
	if (se=='true' and sub=='true'):
		li.setSubtitles([srtsubs_path])
	license_server = 'https://lic.drmtoday.com/license-proxy-widevine/cenc/'
	license_headers = 'dt-custom-data=' + dt_custom_data + '&x-dt-auth-token=' + x_dt_auth_token + '&Origin=https://www.hbogo.ro&Content-Type='
	license_key = license_server + '|' + license_headers + '|R{SSM}|JBlicense'

	protocol = 'ism'
	drm = 'com.widevine.alpha'
	is_helper = inputstreamhelper.Helper(protocol, drm=drm)
	is_helper.check_inputstream()
	li.setProperty('inputstreamaddon', 'inputstream.adaptive')
	li.setProperty('inputstream.adaptive.manifest_type', protocol)
	li.setProperty('inputstream.adaptive.license_type', drm)
	li.setProperty('inputstream.adaptive.license_data', 'ZmtqM2xqYVNkZmFsa3Izag==')
	li.setProperty('inputstream.adaptive.license_key', license_key)

	xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, li)

	#Set external subtitles if this mode is selected
	#if (se=='true' and sub=='true'):
	#	while not xbmc.Player().isPlaying():
	#		xbmc.sleep(42)
	#		xbmc.Player().setSubtitles(srtsubs_path)

def SEARCH():
	keyb = xbmc.Keyboard(search_string, 'Searching movies and series ...')
	keyb.doModal()
	searchText = ''
	if (keyb.isConfirmed()):
		searchText = urllib.quote_plus(keyb.getText())
		if searchText == "":
			addDir('No results','','','',md+'DefaultFolderBack.png')
		else:
			__settings__.setSetting('lastsearch', searchText)

			req = urllib2.Request('https://roapi.hbogo.eu/v8/Search/Json/'+HBOCode+'/ANMO/'+searchText.decode('utf-8', 'ignore').encode('utf-8', 'ignore')+'/0/0/0/0/0/3', None, loggedin_headers)
			opener = urllib2.build_opener()
			f = opener.open(req)
			jsonrsp = json.loads(f.read())
			#print jsonrsp

			try:
				if jsonrsp['ErrorMessage']:
					xbmcgui.Dialog().ok('Error', jsonrsp['ErrorMessage'])
			except:
				pass

			br=0
			for index in range(0, len(jsonrsp['Container'][0]['Contents']['Items'])):
				allowplay = jsonrsp['Container'][0]['Contents']['Items'][index].get( 'AllowPlay', None )
				if (jsonrsp['Container'][0]['Contents']['Items'][index]['ContentType'] == 1 or jsonrsp['Container'][0]['Contents']['Items'][index]['ContentType'] == 7): #1,7=MOVIE/EXTRAS, 2=SERIES(serial), 3=SERIES(episode)
					#Movies
					addLink(jsonrsp['Container'][0]['Contents']['Items'][index]['ObjectUrl'],'',jsonrsp['Container'][0]['Contents']['Items'][index]['AgeRating'],jsonrsp['Container'][0]['Contents']['Items'][index]['ImdbRate'],jsonrsp['Container'][0]['Contents']['Items'][index]['BackgroundUrl'],[jsonrsp['Container'][0]['Contents']['Items'][index]['Cast'].split(', ')][0],jsonrsp['Container'][0]['Contents']['Items'][index]['Director'],jsonrsp['Container'][0]['Contents']['Items'][index]['Writer'],jsonrsp['Container'][0]['Contents']['Items'][index]['Duration'],jsonrsp['Container'][0]['Contents']['Items'][index]['Genre'],jsonrsp['Container'][0]['Contents']['Items'][index]['Name'].encode('utf-8', 'ignore'),jsonrsp['Container'][0]['Contents']['Items'][index]['OriginalName'],jsonrsp['Container'][0]['Contents']['Items'][index]['ProductionYear'],5,'',True)
				elif jsonrsp['Container'][0]['Contents']['Items'][index]['ContentType'] == 3:
					#Episodes
					addLink(jsonrsp['Container'][0]['Contents']['Items'][index]['ObjectUrl'],'',jsonrsp['Container'][0]['Contents']['Items'][index]['AgeRating'],jsonrsp['Container'][0]['Contents']['Items'][index]['ImdbRate'],jsonrsp['Container'][0]['Contents']['Items'][index]['BackgroundUrl'],[jsonrsp['Container'][0]['Contents']['Items'][index]['Cast'].split(', ')][0],jsonrsp['Container'][0]['Contents']['Items'][index]['Director'],jsonrsp['Container'][0]['Contents']['Items'][index]['Writer'],jsonrsp['Container'][0]['Contents']['Items'][index]['Duration'],jsonrsp['Container'][0]['Contents']['Items'][index]['Genre'],jsonrsp['Container'][0]['Contents']['Items'][index]['SeriesName'].encode('utf-8', 'ignore')+' '+jsonrsp['Container'][0]['Contents']['Items'][index]['Name'].encode('utf-8', 'ignore'),jsonrsp['Container'][0]['Contents']['Items'][index]['OriginalName'],jsonrsp['Container'][0]['Contents']['Items'][index]['ProductionYear'],5,'',True)
				else:
					#Series
					addDir(jsonrsp['Container'][0]['Contents']['Items'][index]['Name'].encode('utf-8', 'ignore'),jsonrsp['Container'][0]['Contents']['Items'][index]['ObjectUrl'],'',2,jsonrsp['Container'][0]['Contents']['Items'][index]['BackgroundUrl'])
				br=br+1
			if br==0:
				addDir('No results','','','',md+'DefaultFolderBack.png')

def addLink(ou,plot,ar,imdb,bu,cast,director,writer,duration,genre,name,on,py,mode,date,playble):
	cid = ou.rsplit('/',2)[1]
	u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&cid="+cid+"&thumbnail="+bu
	ok=True
	if playble:
		playble = 'true'
	else:
		playble = 'false'
		u = ''
		name = name + ' - Soon'
	liz=xbmcgui.ListItem(name, iconImage=bu, thumbnailImage=bu)
	liz.setProperty("IsPlayable" , playble)
	liz.setArt({ 'thumb': bu,'poster': bu, 'banner' : bu, 'fanart': bu })
	liz.setInfo( type="Video", infoLabels={'plot': plot, "mpaa": str(ar)+'+', "rating": imdb, "cast": cast, "director": director, "writer": writer, "duration": duration, "genre": genre, "title": name, "originaltitle": on, "year": py, "date": date, 'sorttitle': name , 'aired': date} )
	liz.addStreamInfo('video', { 'width': 1280, 'height': 720 })
	liz.addStreamInfo('video', { 'aspect': 1.78, 'codec': 'h264' })
	liz.addStreamInfo('audio', { 'codec': 'aac', 'channels': 2 })

	contextmenu = []
	contextmenu.append(('Information', 'XBMC.Action(Info)'))
	liz.addContextMenuItems(contextmenu)
	ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=False)
	return ok



#Module for adding a separate directory and its attributes to the contents of the Kodi catalog displayed
def addDir(name,url,plot,mode,iconimage):
	u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
	ok=True
	liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
	liz.setInfo( type="Video", infoLabels={ "Title": name, "Plot": plot } )

	print("plot: "+str(plot.count))
	if len(plot)>0:
		contextmenu = []
		contextmenu.append(('Information', 'XBMC.Action(Info)'))
		liz.addContextMenuItems(contextmenu)

	ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
	return ok


def get_params():
	param=[]
	paramstring=sys.argv[2]
	if len(paramstring)>=2:
		params=sys.argv[2]
		cleanedparams=params.replace('?','')
		if (params[len(params)-1]=='/'):
			params=params[0:len(params)-2]
		pairsofparams=cleanedparams.split('&')
		param={}
		for i in range(len(pairsofparams)):
			splitparams={}
			splitparams=pairsofparams[i].split('=')
			if (len(splitparams))==2:
				param[splitparams[0]]=splitparams[1]
	return param

params=get_params()
url=None
name=None
iconimage=None
mode=None
ssl._create_default_https_context = ssl._create_unverified_context
try:
		url=urllib.unquote_plus(params["url"])
except:
		pass
try:
		name=urllib.unquote_plus(params["name"])
except:
		pass
try:
		thumbnail=str(params["thumbnail"])
except:
		pass
try:
		mode=int(params["mode"])
except:
		pass
try:
		cid=str(params["cid"])
except:
		pass


#The list of individual modules in this plugin - must fully correspond to the above code
if mode==None or url==None or len(url)<1:
		CATEGORIES()

elif mode==1:
		LIST(url)

elif mode==2:
		SEASON(url)

elif mode==3:
		EPISODE(url)

elif mode==4:
		SEARCH()

elif mode==5:
		PLAY(url)

elif mode==6:
		SILENTREGISTER()

elif mode==7:
		LOGIN()


xbmcplugin.endOfDirectory(int(sys.argv[1]))
