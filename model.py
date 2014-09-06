from google.appengine.ext import ndb

class UserProfile(ndb.Model):
	"""Models the profile (JSON) of an individual user."""
	profile = ndb.TextProperty()
	date = ndb.DateTimeProperty(auto_now_add=True)

class UserSnippet(ndb.Model):
	"""NDB model for a user weekly snippet.
		Since we are in a given domain, we will use the login name as the key.
		`arnaud@thegovlab.org` will have `arnaud` as the key.
	"""
	content = ndb.TextProperty()