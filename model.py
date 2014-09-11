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

class UserProject(ndb.Model):
	"""NDB model for a project."""
	shortName = ndb.StringProperty(required=True)
	title = ndb.StringProperty(required=False)
	description = ndb.TextProperty(indexed=True, required=True)
	members = ndb.StringProperty(repeated=True)
	publicFolder = ndb.StringProperty()
	teamFolder = ndb.StringProperty()
	blogURL = ndb.StringProperty()

	def getTeamGroup(self):
		"""Returns the name of the Google Group for team members of this project."""
		return "proj-%s-team"

	def getDiscussGroup(self):
		"""Returns the name of the Google Group for discussion on this project."""
		return "proj-%s-discuss"