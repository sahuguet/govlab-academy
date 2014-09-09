
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
from google.appengine.api import memcache

if os.environ['SERVER_SOFTWARE'].startswith('Development'):
	import account_services_dev as govlab
else:
	import account_services as govlab

from apiclient.errors import HttpError

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

def getUserMapping():
	logging.info('Inside getUserMapping().')
	userMapping = memcache.get('__USER_MAPPING__')
	if userMapping is not None:
		logging.info('Info in memcache')
		return userMapping
	else:
		logging.info('populating memcache')
		credentials = SignedJwtAssertionCredentials(SERVICE_ACCOUNT_EMAIL,
				key,
				scope=DIRECTORY_SCOPES,
				sub=USER_DELEGATION)
		http = httplib2.Http()
		http = credentials.authorize(http)
		service = build('admin', 'directory_v1', http=http)
		userMapping = {}
		for user in service.users().list(domain='thegovlab.org', maxResults=500, orderBy='familyName').execute()['users']:
			userMapping[user['primaryEmail']] = user['name']['fullName']
		memcache.add('__USER_MAPPING__', userMapping)
		return userMapping

def getUserProfile(userid):
	credentials = SignedJwtAssertionCredentials(SERVICE_ACCOUNT_EMAIL,
			key,
			scope=DIRECTORY_SCOPES,
			sub=USER_DELEGATION)
	http = httplib2.Http()
	http = credentials.authorize(http)
	service = build('admin', 'directory_v1', http=http)
	try:
		return service.users().get(userKey=userid).execute()
	except HttpError, e:
		return None

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
		faculty = []
		for user in service.users().list(domain='thegovlab.org', maxResults=500, orderBy='familyName').execute()['users']:
			if user['orgUnitPath'] == '/The GovLab Academy/SPPT Fall 2014/MIT':
				mit_students.append(user)
			if user['orgUnitPath'] == '/The GovLab Academy/SPPT Fall 2014/NYU':
				nyu_students.append(user)
			if user['orgUnitPath'] == '/The GovLab Academy/SPPT Fall 2014/Online':
				online_students.append(user)
			if user['primaryEmail'].split('@')[0] in [ 'arnaud', 'noveck', 'alan', 'nikki' ]:
				faculty.append(user)
		logging.info(mit_students)
		template = JINJA_ENVIRONMENT.get_template('templates/class_roster.html')
		sortStudents = lambda x:x['name']['familyName']
		template_values = {
		'me': user_profile_govlab,
		#'mit_students': sorted(mit_students, key=sortStudents),
		#'nyu_students': sorted(nyu_students, key=sortStudents),
		#'online_students': sorted(online_students, key=sortStudents)
		'faculty': faculty,
		'mit_students': mit_students,
		'nyu_students': nyu_students,
		'online_students': online_students }
		self.response.out.write(template.render(template_values))

app = webapp2.WSGIApplication([
	('/fall-2014-class', AllUsersHandler),
	], debug=True)