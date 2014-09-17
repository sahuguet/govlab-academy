import jinja2
import json
import logging
from model import UserProfile
import os
from google.appengine.api import memcache
 
def fixEmail(email):
	"""GMail users get their email truncated with missing @gmail.com"""
	if len(email.split('@')) != 2:
		return email + '@gmail.com'
	else:
		return email

ACADEMY_ADMINS = [ 'arnaud@thegovlab.org', 'nikki@thegovlab.org' ]

def userCanEditProject(email, project):
	email = fixEmail(email)
	return email in project.members or email in ACADEMY_ADMINS

def getUserProfile(email):
	return UserProfile.get_by_id(fixEmail(email))

def invalidUser(email):
	return getUserProfile(email) == None

def validUser(email):
	return getUserProfile(email) != None

USER_MAPPING = None
def getUsersMapping():
	"""Returns a dictionary: email -> { fname, lname, photo, affiliation }.
	- level 1 caching = global variable.
	- level 2 caching = memcache
	"""
	USER_MAPPING_MEMCACHE_KEY = '__USER_MAPPING__'
	global USER_MAPPING
	if USER_MAPPING:
		return USER_MAPPING
	__user_mapping__ = memcache.get(USER_MAPPING_MEMCACHE_KEY)
	if __user_mapping__:
		logging.info('USER_MAPPING already set.')
		USER_MAPPING = __user_mapping__
		return __user_mapping__
	logging.info('Building USER_MAPPING.')
	all_users = UserProfile.query().fetch(limit=500)
	users_mapping = {}
	for u in all_users:
		users_mapping[u.key.id()] = u
		#{
		#'fname': u.fname, 'lname': u.lname,
		#'photoURL': u.photoUrl, 'affiliation': u.affiliation }
	memcache.add(USER_MAPPING, users_mapping)
	USER_MAPPING = users_mapping
	logging.info(users_mapping)
	return users_mapping

def createNewUser(fname, lname, email, affiliation):
	if UserProfile.get_by_id(email):
		logging.error("User %s already exists." % email)
		return
	user_profile = UserProfile(id=email, fname=fname, lname=lname, affiliation=affiliation)
	user_profile.put()
	logging.info("New user %s created." % email)

""" JINJA2 set-up """

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

# We define a bunch of filters to make the templates simpler and catch bad data.
JINJA_ENVIRONMENT.filters['getProfile'] = lambda x: getUsersMapping().setdefault(x, x)
JINJA_ENVIRONMENT.filters['fullName'] = lambda x: "%s %s" % (x.fname, x.lname) if type(x) is UserProfile else x
JINJA_ENVIRONMENT.filters['affiliation'] = lambda x: "%s" % x.affiliation if type(x) is UserProfile else 'N/A'
JINJA_ENVIRONMENT.filters['photoUrl'] = lambda x: x.photoUrl
JINJA_ENVIRONMENT.filters['defaultPicture'] = lambda x: x if x or x!=None else '/assets/silhouette200.png'
JINJA_ENVIRONMENT.filters['primaryEmail'] = lambda x: x.key.id()
JINJA_ENVIRONMENT.filters['projectId'] = lambda x: x.key.id()

get_template = JINJA_ENVIRONMENT.get_template

""" END of JINJA2 set-up """