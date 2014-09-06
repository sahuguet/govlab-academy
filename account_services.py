
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), "libs"))

import logging
import httplib2
from apiclient.discovery import build
from oauth2client.client import SignedJwtAssertionCredentials
import jinja2
import webapp2
from google.appengine.api import users

if os.environ['SERVER_SOFTWARE'].startswith('Development'):
	import account_services_dev as govlab
else:
	import account_services as govlab

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

def getUserProfile(userid):
	credentials = SignedJwtAssertionCredentials(SERVICE_ACCOUNT_EMAIL,
			key,
			scope=DIRECTORY_SCOPES,
			sub=USER_DELEGATION)
	http = httplib2.Http()
	http = credentials.authorize(http)
	service = build('admin', 'directory_v1', http=http)
	return service.users().get(userKey=userid).execute()

class AllUsersHandler(webapp2.RequestHandler):
	def get(self):
		user = users.get_current_user()
		user_profile_govlab = govlab.getUserProfile(user.email())
		credentials = SignedJwtAssertionCredentials(SERVICE_ACCOUNT_EMAIL,
			key,
			scope=DIRECTORY_SCOPES,
			sub=USER_DELEGATION)
		http = httplib2.Http()
		http = credentials.authorize(http)
		service = build('admin', 'directory_v1', http=http)

		mit_students = []
		nyu_students = []
		online_students = []
		for user in service.users().list(domain='thegovlab.org').execute()['users']:
			if user['orgUnitPath'] == '/The GovLab Academy/SPPT Fall 2014/MIT':
				mit_students.append(user)
			if user['orgUnitPath'] == '/The GovLab Academy/SPPT Fall 2014/NYU':
				nyu_students.append(user)
			if user['orgUnitPath'] == '/The GovLab Academy/SPPT Fall 2014/Online':
				online_students.append(user)
		logging.info(mit_students)
		template = JINJA_ENVIRONMENT.get_template('templates/class_roster.html')
		sortStudents = lambda x:x['name']['familyName']
		template_values = {
		'user': user_profile_govlab,
		'mit_students': sorted(mit_students, key=sortStudents),
		'nyu_students': sorted(nyu_students, key=sortStudents),
		'online_students': sorted(online_students, key=sortStudents) }
		self.response.out.write(template.render(template_values))

app = webapp2.WSGIApplication([
	('/fall-2014-class', AllUsersHandler),
	], debug=True)