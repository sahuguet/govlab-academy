
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), "libs"))

import logging
import httplib2
from apiclient.discovery import build
from oauth2client.client import SignedJwtAssertionCredentials
import jinja2
import webapp2


# Email of the Service Account.
SERVICE_ACCOUNT_EMAIL = '436251601698-nt1t0h4avvi0hu5udap80e0mrn3nl56d@developer.gserviceaccount.com'
# Path to the Service Account's Private Key file.
SERVICE_ACCOUNT_PKCS12_FILE_PATH = '__SECRETS__/govlabacademy.pem' # AppEngine only understand .pem.

DIRECTORY_SCOPES = ['https://www.googleapis.com/auth/admin.directory.user',
										'https://www.googleapis.com/auth/admin.directory.group']
USER_DELEGATION = 'arnaud@thegovlab.org'

f = file(SERVICE_ACCOUNT_PKCS12_FILE_PATH, 'rb')
key = f.read()
f.close()

JINJA_ENVIRONMENT = jinja2.Environment(
	loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
  extensions=['jinja2.ext.autoescape'],
  autoescape=True)

class AllUsersHandler(webapp2.RequestHandler):
	def get(self):
		credentials = SignedJwtAssertionCredentials(SERVICE_ACCOUNT_EMAIL,
			key,
			scope=DIRECTORY_SCOPES,
			sub=USER_DELEGATION)
		http = httplib2.Http()
		http = credentials.authorize(http)
		service = build('admin', 'directory_v1', http=http)
		users = []
		for user in service.users().list(domain='thegovlab.org').execute()['users']:
			if user['orgUnitPath'] == '/':
				users.append(user)
		alums = []
		for user in service.users().list(domain='thegovlab.org').execute()['users']:
			logging.info(user)
			if user['orgUnitPath'] == '/Alumni':
				alums.append(user)
		groups = []
		for group in service.groups().list(domain='thegovlab.org').execute()['groups']:
			groups.append(group)
		members = []
		for member in service.members().list(groupKey='academy@thegovlab.org').execute()['members']:
			members.append(member['email'])
		template = JINJA_ENVIRONMENT.get_template('templates/all_users.html')
		template_values = { 'users': users,
		'alums': alums,
		'groups': groups,
		'members': members }
		self.response.out.write(template.render(template_values))

app = webapp2.WSGIApplication([
	('/allusers', AllUsersHandler),
	], debug=True)