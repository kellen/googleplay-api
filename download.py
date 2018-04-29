from gpapi.googleplay import GooglePlayAPI, RequestError

import getpass
import cmd
import sys
import argparse
import configparser

ap = argparse.ArgumentParser(description='Test download of expansion files')
ap.add_argument('-c', '--config', dest='configfile', help='config file to use')
ap.add_argument('-p', '--package', dest='package', help="package to download")
args = ap.parse_args()

CONFIG_SECTION = "apk-downloader"
CONFIG_GSFID = "gsfId"
CONFIG_AUTHSUBTOKEN = "authSubToken"

SERVER_LOCALE = "en_US"
SERVER_TZ = "America/New_York"

with open(args.configfile, 'rw+') as configfile:
	config = configparser.SafeConfigParser()
	config.readfp(configfile)

	try:
		gsfId = config.get(CONFIG_SECTION, CONFIG_GSFID)
		authSubToken = config.get(CONFIG_SECTION, CONFIG_AUTHSUBTOKEN)
	except configparser.NoOptionError:
		print "Missing one of gsfId or authSubToken, fetching new..."
		email = raw_input("Enter email: ")
		password = getpass.getpass("Enter password: ")

		server = GooglePlayAPI(SERVER_LOCALE, SERVER_TZ)
		server.login(args.email, args.password, None, None)
		gsfId = server.gsfId
		authSubToken = server.authSubToken
		
		# write fetched values to config
		config.set(CONFIG_SECTION, CONFIG_GSFID, gsfId)
		config.set(CONFIG_SECTION, CONFIG_AUTHSUBTOKEN, authSubToken)

		config.write(configfile)

server = GooglePlayAPI(SERVER_LOCALE, SERVER_TZ)
server.login(None, None, gsfId, authSubToken)

app = server.details(args.package)
docid = app['docId']
filename = docid + ".apk"
print "Fetching docId", docid, "to file", filename

fl = server.download(docid)
with open(filename, 'wb') as apk_file:
    for chunk in fl.get('file').get('data'):
        apk_file.write(chunk)
    print('\nDownload successful\n')
