from google.appengine.ext import ndb

class UserProfile(ndb.Model):
	"""Models the profile (JSON) of an individual user."""
	profile = ndb.TextProperty()
	date = ndb.DateTimeProperty(auto_now_add=True)