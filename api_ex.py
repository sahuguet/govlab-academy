import sys
import csv
import glob
import json
import re
sys.path.append('/usr/local/google_appengine')
for l in glob.glob("/usr/local/google_appengine/lib/*"):
	sys.path.append(l)

from google.appengine.ext.remote_api import remote_api_stub
from google.appengine.ext import ndb
from google.appengine.api import mail

from model import UserProfile
from model import UserProject
import getpass

def auth_func():
	password = 'ockbozzqkzeynkak'
  #return (raw_input('Username:'), getpass.getpass('Password:'))
	return ('arnaud@thegovlab.org', password)

remote_api_stub.ConfigureRemoteApi(None, '/_ah/remote_api', auth_func,
	#'govlab-dev.appspot.com',
 	# 'govlabacademy.appspot.com',
  'govlabacademy2.appspot.com'
  )

def sendInvite(fname, username, user_email):
	print >> sys.stderr, "Hi %s, new account = % s; message sent to %s" % (fname, username, user_email)
	message = mail.EmailMessage(sender="nikki@thegovlab.org", subject="Welcome to the GovLab Academy class")
	message.to = user_email
	message.bcc = "nikki@thegovlab.org"
	message.body = """
Hi %(fname)s,

We just created an account for you on thegovlab.org domain.
Your username (and email address) is %(username)s.
This is the address you should use to access resources and communicate in the context of the class.

You can sign-in as %(username)s at http://www.google.com/a/thegovlab.org .
Your default password is: %(password)s.

Please follow the instructions from Google to claim your account.

Once you are done, you can access the GovLab Academy web site at http://academy.thegovlab.org.
Bookmarking the link might be a good idea.

The Academy website gives you access to resources and tools that will be useful for the class.
Please update your profile information (http://academy.thegovlab.org/profile).
This way, other participants of the course will be able to learn about you and connect with you.

For any questions or comments, use the listserv and/or submit them via the feedback tab on the website (bottom right of each page).

Best,

Nikki

""" % { 'fname': fname, 'username': username, 'password': 'changeme' }
	message.send()
	print >> sys.stderr, "message sent to %s" % user_email


def sendInvites():
	with open('F2014-students_tmp.csv', 'rb') as csvfile:
		reader = csv.reader(csvfile)
		for row in reader:
			lname = row[0]
			fname = row[1]
			email = row[2]
			if email == "":
				print >> sys.stderr, "Skipping %s" % row
				continue
			sendInvite(fname, "%s@thegovlab.org" % email.split('@')[0], email)
			print >> sys.stderr, "User %s invited." % email

def populateProfiles():
	with open('F2014-applications.csv', 'rb') as csvfile:
		reader = csv.reader(csvfile)
		count = 1
		for row in reader:
			#if count == 0:
			#	break
			if len(row[3].split('@')) != 2 :
				print >> sys.stderr, "Skipping %s" % row
				continue
			lname = row[1]
			fname = row[2]
			email = row[3].split('@')[0] + '@thegovlab.org'
			credentials = row[7] # credentials
			experience = row[8] # experience
			skills = row[9] # skills
			interests = row[10] # interests
			bio = row[6] # bio
			location = row[14] # location
			country = row[16] # country
			if row[19] != "yes":
				print >> sys.stderr, "Skipping %s because of missing letter." % email
			user_profile = UserProfile.get_by_id(email)
			profile_data = { 'fname': fname, 'lname': lname,
				'offer': skills, 'demand': interests,
				'experience': experience, 'expertise': credentials,
				'city_state': location, 'country': country  }
			if user_profile == None:
				user_profile = UserProfile(id=email, profile=json.dumps(profile_data))
				user_profile.put()
			else:
				print >> sys.stderr, "Skipping %s because data is already there." % email
				continue
			print >> sys.stderr, "Profile for user %s added." % email	
			count = count - 1

def populateTestProject():
	project = UserProject(id="govlab-academy",
		shortName="govlab-academy",
		title="The GovLab Academy",
		description="An online learning platform for change agents and civic innovators",
		members=map(lambda x: "%s@thegovlab.org" %x, ['arnaud', 'nikki', 'lisbeth', 'noveck', 'alan']))
	project.put()
	print >> sys.stderr, "Project added."

#populateTestProject()
#print UserProject.query(UserProject.members=='arnaud').fetch()

def processProjectName(str):
	"""We replace everything that's not a-z or 0-9 or - or _."""
	str = str.lower()
	str = re.sub('[^a-z-_0-9]', '-', str)
	return str

def populateProjects():
	projects = {}
	with open('F2014-projects.csv', 'rb') as csvfile:
		reader = csv.reader(csvfile)
		count = 1
		for row in reader:
			if len(row[2].split('@')) != 2 :
				print >> sys.stderr, "Skipping %s" % row
				continue
			member = row[2].split('@')[0]
			project_shortname = row[13]
			if row[13] == "":
				print >> sys.stderr, "Skipping project for %s because no name." % member
				continue
			project_shortname = processProjectName(row[13])
			projects.setdefault(project_shortname, {'title': row[13], 'members': []})['members'].append(member)
	print "%d projects." % len(projects)
	for k, v in projects.iteritems():
		project = UserProject(id=k,
			shortName=k,
			title=v['title'],
			description="...",
			members=v['members'])
		project.put()

"""
		project = UserProject(id="prison-break",
			shortName="prison-break",
			title="Improving the lives of inmates",
			description="...",
			members=['arnaud', 'nikki', 'lisbeth'])
		project.put()
	print >> sys.stderr, "Project added."
"""
#populateTestProject()

def checkUser(email):
	return UserProfile.get_by_id(email) != None

#createNewUser('Arnaud', 'Sahuguet', 'arnaud.sahuguet@gmail.com', 'GovLab')
#print checkUser('arnaud.sahuguet@gmail.com')
#print checkUser('arnaud.sahuguet2@gmail.com')
from domain_services import *
#createNewUser('Lisbeth', 'Salander', 'lisbeth@thegovlab.org', 'NYU')
#createNewUser('Arnaud', 'Sahuguet', 'arnaud@thegovlab.org', 'GovLab')
#createNewUser('Arnaud', 'Sahuguet', 'arnaud.sahuguet@gmail.com', 'MIT')
#createNewUser('Mikael', 'Blomkvist', 'mikael@thegovlab.org', 'MIT')

#print getUsersMapping()

#for user in UserProfile.query().order(UserProfile.lname, UserProfile.fname).fetch(limit=500):
#	print user
#	print type(user) is UserProfile
#populateTestProject()

#createNewUser('Nikki', 'Zeichner', 'nikzei@gmail.com', 'NYU')
#createNewUser('Nikki', 'Zeichner', 'nikki@thegovlab.org', 'GovLab')
#createNewUser('Lauren', 'Yu', 'lauren.r.yu@gmail.com', 'NYU')
#createNewUser('Lauren', 'Yu', 'lauren@thegovlab.org', 'GovLab')

def createProject(shortname, title, description):
	p = UserProject(shortName=shortname, title=title, description=description)
	p.put()
	print p

#createProject("my-project", "my cool project", "this is a really cool project")
import httplib2
from apiclient.discovery import build
from oauth2client.client import SignedJwtAssertionCredentials
SERVICE_ACCOUNT_EMAIL = '56603619214-lfu9ipb0p4ba1k3hru846rf4gmp41vjh@developer.gserviceaccount.com'
SERVICE_ACCOUNT_PKCS12_FILE_PATH = '__SECRETS__/govlabacademy.p12'
USER_DELEGATION = 'arnaud@thegovlab.org'
f = file(SERVICE_ACCOUNT_PKCS12_FILE_PATH, 'rb')
key = f.read()
f.close()
credentials = SignedJwtAssertionCredentials(SERVICE_ACCOUNT_EMAIL,
	key,
	scope=['https://www.googleapis.com/auth/admin.directory.group'],
	sub=USER_DELEGATION)
http = httplib2.Http()
http = credentials.authorize(http)
service = build('admin', 'directory_v1', http=http)

#for group in service.groups().list(domain='thegovlab.org').execute()['groups']:
#	print group

THE_GROUP = 'sppwt-f2014-class@thegovlab.org'

import apiclient.errors

def addUserToGroup(email):
	try:
		service.members().insert(groupKey=THE_GROUP, body={ "kind": "admin#directory#member", "email": email }).execute()
	except apiclient.errors.HttpError, e:
		print >> sys.stderr, e				
	print >> sys.stderr, "User %s added." % email

#addUserToGroup('lisbeth@thegovlab.org')

def createUsers(addToGroup=False):
	count = 0
	with open('academy-fall2014-all.csv', 'rb') as csvfile:
		reader = csv.reader(csvfile)
		for row in reader:
			lname = row[0].strip()
			fname = row[1].strip()
			email = row[2].strip()
			affiliation = row[3]
			if affiliation == "ITP":
				affiliation = 'NYU'
			if 'Online' in affiliation:
				affiliation = 'online'
			if len(email.split('@')) != 2:
				print >> sys.stderr, "Not a valid entry: %s" % row
				continue
			createNewUser(fname, lname, email, affiliation)
			if addToGroup:
				addUserToGroup(email)
			print >> sys.stderr, "Processing %s (%s)" % (email, affiliation)
			count = count + 1
	print "%d users created." % count

#createUsers()
import random
import string



def createProjectsAndTeams():
	with open('academy-fall2014-all.csv', 'rb') as csvfile:
		reader = csv.reader(csvfile)
		projects = {}
		for row in reader:
			email = row[2].strip()
			if len(email.split('@')) != 2:
				print >> sys.stderr, "Not a valid entry: %s" % row
				continue
			team = row[12].strip()
			topic = row[10]
			if team == "":
				team = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
			if team in projects:
				projects[team]['members'].append(email)
			else:
				projects[team] = { 'title': topic, 'members': [ email ] }
	for key, proj in projects.iteritems():
		p = UserProject(title=proj['title'], description="project of %s" % ",".join(proj['members']), members=proj['members'])
		p.put()
		print "Project created"

#createProjectsAndTeams()
#p = UserProject(title='arnaud test', description='nothing yet')
#p.put()
#print p.key()
#print UserProject.get_by_id(5649391675244544)

#print getUserProfile('Cheryl.Murray@houstonpolice.org')
#print getUserProfile('arnaud@thegovlab.org')

#for user in UserProfile.query().order(UserProfile.lname, UserProfile.fname).fetch(limit=500):
#	print user
"""
createNewUser('Alan', 'Kantrow', 'alan@thegovlab.org', 'GovLab')
createNewUser('Beth', 'Noveck', 'noveck@thegovlab.org', 'GovLab')
createNewUser('Arnaud', 'Sahuguet', 'arnaud@thegovlab.org', 'GovLab')
createNewUser('Nikki', 'Zeichner', 'nikki@thegovlab.org', 'GovLab')
createUsers()
"""

def migrateProfiles():
	with open('academy-fall2014-all.csv', 'rb') as csvfile:
		reader = csv.reader(csvfile)
		mapping = {}
		for row in reader:
			email = row[2].strip()
			if len(email.split('@')) != 2:
				print >> sys.stderr, "Not a valid entry: %s" % row
				continue
			mapping[email.split('@')[0] + '@thegovlab.org'] = email
	all_users = json.loads(open('all_users.json').read())
	for k,v in all_users.iteritems():
		if k in mapping:
			profile = UserProfile.get_by_id(mapping[k])
			if profile == None:
				print >> sys.stderr, "Cannot find user %s." % mapping[k]
				continue
			profile.profile = json.dumps(v)
			profile.put()
			print "Assigned data to user %s" % mapping[k]

#json.loads(open('all_users.json').read())
#migrateProfiles()
#createNewUser('Arnaud', 'Sahuguet', 'arnaud@thegovlab.org', 'GovLab')

"""
createNewUser('Erik', 'Johnston', 'erik.johnston@asu.edu', 'GovLab')
addUserToGroup('erik.johnston@asu.edu')
createNewUser('Carmen', 'Abrego', 'Carmen.abrego@houstontx.gov', 'online')
addUserToGroup('Carmen.abrego@houstontx.gov')
createNewUser('Pedro', 'Fonseca', 'pedro.fonseca@houstontx.gov', 'online')
addUserToGroup('pedro.fonseca@houstontx.gov')
createNewUser('Rhea', 'Lawson', 'rhea.lawson@houstontx.gov', 'online')
addUserToGroup('rhea.lawson@houstontx.gov')
createNewUser('Jennifer', 'Schwartz', 'jennifer.schwartz@houstontx.gov', 'online')
addUserToGroup('jennifer.schwartz@houstontx.gov')
createNewUser('Steven', 'Griner', 'sgriner@oas.org', 'online')
addUserToGroup('sgriner@oas.org')
"""

#createNewUser('Carmen', 'Abrego', 'Carmen.abrego@houstontx.gov', 'online')
#p = UserProject.get_by_id(5253860620763136)
#p.members = p.members + ['carmen.abrego@houstontx.gov', 'pedro.fonseca@houstontx.gov', 'jennifer.schwartz@houstontx.gov' ]
#p.put()

"""
for user in UserProfile.query().fetch(limit=500):
	email = user.key.id()
	if email != email.lower():
		print >> sys.stderr, "We need to delete the entity."
		#new_user = UserProfile(id=email.lower(),
		#	fname=user.fname, lname=user.lname,
		#	affiliation=user.affiliation, photoUrl=user.photoUrl,
		#	profile=user.profile)
		#new_user.put()
		user.key.delete()

for p in UserProject.query().fetch(limit=500):
	members = p.members
	p.members = map( lambda x: x.lower(), members)
	p.put()
"""
"""
createNewUser('Lisbeth', 'Salander', 'lisbeth@thegovlab.org', 'NYU')
createNewUser('Arnaud', 'Sahuguet', 'arnaud@thegovlab.org', 'online')
createNewUser('Mikael', 'Blomkvist', 'mikael@thegovlab.org', 'MIT')
project = UserProject(title='The GovLab Academy', description='On-line learning for civic innovators', members=['arnaud@thegovlab.org', 'lisbeth@thegovlab.org', 'mikael@thegovlab.org'])
project.put()
"""

#createNewUser('Pedro', 'Prieto Martin', 'hcprieto@gmail.com', 'online')
#project = UserProject(title='crowdsourced civic open data', description='TBD', members=['hcprieto@gmail.com'])
#project.put()
def migrateUser(old_email, new_email):
	old_user = UserProfile.get_by_id(old_email)
	print old_user
	new_user = createNewUser(old_user.fname, old_user.lname, new_email, old_user.affiliation)
	new_user.profile = old_user.profile
	new_user.put()
	old_user.key.delete()

#migrateUser('jennifer_groff@mail.harvard.edu', 'jsg943@mail.harvard.edu')
#project = UserProject.get_by_id(6384721483268096)
#project.members = ['jsg943@mail.harvard.edu']
#project.put()

#createNewUser('Luis', 'Daniel', 'luis@thegovlab.org', 'GovLab')
#migrateUser('yw1436@stern.nyu.edu', 'yw1436@nyu.edu')
migrateUser('jsg943@mail.harvard.edu', 'jsgroff@gmail.com')

def removeUser(email):
	p = UserProject.query(UserProject.members == email).get()
	p.members.remove('mikael@thegovlab.org')
	p.put()
	if p.members == []:
		# If only member, then we remove the project.
		p.key.delete()
	u = UserProfile.query(UserProfile.email == email).get()
	u.key.delete()
