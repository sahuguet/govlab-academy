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

createNewUser('Nikki', 'Zeichner', 'nikzei@gmail.com', 'NYU')
createNewUser('Nikki', 'Zeichner', 'nikki@thegovlab.org', 'GovLab')
createNewUser('Lauren', 'Yu', 'lauren.r.yu@gmail.com', 'NYU')
createNewUser('Lauren', 'Yu', 'lauren@thegovlab.org', 'GovLab')


