from google.appengine.ext import ndb

class UserProfile(ndb.Model):
	"""Models the profile (JSON) of an individual user."""
	# email is the key for each user.
	profile = ndb.TextProperty()
	fname = ndb.StringProperty(required=True)
	lname = ndb.StringProperty(required=True)
	affiliation = ndb.StringProperty(required=True) # e.g. NYU, MIT, online, govlab.
	photoUrl = ndb.StringProperty()
	date = ndb.DateTimeProperty(auto_now_add=True)

	@staticmethod
	def getFields():
		return [ 'city_state', 'country',
		'facebook', 'twitter', 'github', 'linkedin',
		'year_experience', 'sector_experience', 'expertise', 'experience', 'offer', 'demand' ]

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

class ProjectCanvas(ndb.Model):
	"""NDB model for the project canvas.
		Still not clear if this per user of per project.
		Also, might need a time component to it; one canvas per week.
		TODO (arnaud): figure out which is which.
	"""
	content = ndb.TextProperty()

	# We define the fields: canvas_question_[1-20] and pixar_[1-5]
	@staticmethod
	def getFields():
		return [ "canvas_question_%d" % k for k in range(1,21)] + [ "pixar_%d" % k for k in range(1,6) ]