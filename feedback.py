from google.appengine.ext import ndb
from datetime import datetime
from datetime import timedelta
import logging

import webapp2
import os

import jinja2
import json

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

"""A few things worth mentioning:
- you MUST define an OPTIONS method for CORS.
- your post method  MUST return the CORS header.
- your POST methods MUST return null.
- you get the posted content using request.body.
"""

class UserFeedback(ndb.Model):
  """Models the feedback (JSON) of an individual user."""
  feedback = ndb.TextProperty()
  date = ndb.DateTimeProperty(auto_now_add=True)

class ViewFeedbackHandler(webapp2.RequestHandler):
	def get(self):
		# We get all the feedback.
		# We show it in a template.
		query = UserFeedback.query()
		feedbackItems = []
		for item in query.fetch():
			logging.info(item.date)
			logging.info(item.feedback)
			feedbackItems.append({ 'date': item.date, 'content': json.loads(item.feedback) })
		template = JINJA_ENVIRONMENT.get_template('templates/viewFeedback.html')
		self.response.write(template.render({ 'items': feedbackItems }))

class FeedbackHandler(webapp2.RequestHandler):
	def post(self):
		feedback_data = self.request.body
		logging.info(feedback_data)
		user_feedback = UserFeedback(feedback=feedback_data)
		user_feedback.put()
		logging.info("Feedback stored.")
		self.response.headers['Access-Control-Allow-Origin'] = '*'
		self.response.headers['Content-Type'] = 'application/json'
		self.response.write('null')

	def options(self):
		self.response.headers['Access-Control-Allow-Origin'] = '*'
		self.response.headers['Access-Control-Allow-Headers'] = 'Origin, X-Requested-With, Content-Type, Accept'
		self.response.headers['Access-Control-Allow-Methods'] = 'POST, GET, PUT, DELETE'

app = webapp2.WSGIApplication([
	('/feedback', FeedbackHandler),
	('/viewFeedback', ViewFeedbackHandler),
], debug=True)