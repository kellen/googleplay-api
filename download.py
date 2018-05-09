import sys

if sys.version_info[0] != 3 or sys.version_info[1] < 5:
    print("This script requires Python version 3.5 or greater")
    sys.exit(1)

from gpapi.googleplay import GooglePlayAPI, RequestError
import getpass
import cmd
import argparse
import configparser

ap = argparse.ArgumentParser(description='Test download of expansion files')
ap.add_argument('-c', '--config', dest='configfile', help='config file to use', required=True)
ap.add_argument('-d', '--device-codename', dest='devicecode', help='device codename', required=True)
ap.add_argument('-p', '--package', dest='package', help="package to download", required=True)
args = ap.parse_args()

CONFIG_SECTION = "apk-downloader"
CONFIG_GSFID = "gsfId"
CONFIG_AUTHSUBTOKEN = "authSubToken"

SERVER_LOCALE = "en_US"
SERVER_TZ = "America/New_York"

with open(args.configfile, 'r+') as configfile:
	config = configparser.SafeConfigParser()
	config.readfp(configfile)

	try:
		gsfId = config.get(CONFIG_SECTION, CONFIG_GSFID)
		authSubToken = config.get(CONFIG_SECTION, CONFIG_AUTHSUBTOKEN)
	except (configparser.NoOptionError, configparser.NoSectionError):
		print("Missing one of gsfId or authSubToken, fetching new...")
		email = input("Enter email: ")
		password = getpass.getpass("Enter password: ")

		server = GooglePlayAPI(SERVER_LOCALE, SERVER_TZ, device_codename = args.devicecode)
		server.login(email, password, None, None)
		gsfId = str(server.gsfId)
		authSubToken = server.authSubToken
		
		if not config.has_section(CONFIG_SECTION):
			config.add_section(CONFIG_SECTION)
		# write fetched values to config
		config.set(CONFIG_SECTION, CONFIG_GSFID, gsfId)
		config.set(CONFIG_SECTION, CONFIG_AUTHSUBTOKEN, str(authSubToken))

		config.write(configfile)

server = GooglePlayAPI(SERVER_LOCALE, SERVER_TZ, device_codename = args.devicecode)
server.login(None, None, int(gsfId), authSubToken)

app = server.details(args.package)
docid = app['docId']
ver = app["versionString"]
filename = docid + "-" + ver + ".apk"
print("Fetching docId", docid, "to file", filename)
#print(app)

fl = server.download(docid)
with open(filename, 'wb') as apk_file:
    for chunk in fl.get('file').get('data'):
        apk_file.write(chunk)
    print('\nDownload successful\n')
