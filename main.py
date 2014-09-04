#!/usr/bin/env python
import os
import logging
from google.appengine.api import mail
import webapp2
import jinja2
from google.appengine.api import users
#import account_services

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

class InvitationHandler(webapp2.RequestHandler):
	def get(self):
		message = mail.EmailMessage()
		message.sender = 'arnaud@thegovlab.org'
		message.to = 'arnaud.sahuguet@gmail.com'
		message.body = """
I've invited you to Example.com!

To accept this invitation, click the following link,
or copy and paste the URL into your browser's address
bar:

%s""" % "you have been invited."
		message.send()
		self.response.write('email sent')

class AddUserHandler(webapp2.RequestHandler):
	def get(self):
		template = JINJA_ENVIRONMENT.get_template('templates/user_management.html')
		self.response.out.write(template.render({}))

	def post(self):
		data = self.request.get('users')
		users = []
		logging.info(data)
		for line in data.split('\n'):
			if line.startswith('#'):
				continue
			line = line.strip()
			logging.info(line)
			(fname, lname, affiliation, team) = line.split(',')
			if affiliation not in ['nyu', 'mit']:
				affiliation = 'online'
			users.append({'fname': fname, 'lname': lname, 'affiliation': affiliation, 'team': team})
		self.response.out.write(users)

class MainHandler(webapp2.RequestHandler):
	def get(self, page):
		user = users.get_current_user()
		logging.info("page:>>%s<<" % page)
		logging.info("user:>>%s<<" % user)
		template_page = page
		if page is None or page == "":
			if user:
				template_page = 'dashboard'
			else:
				template_page = 'academy'
		page_template = JINJA_ENVIRONMENT.get_template('templates/%s.html' % template_page)
		user_profile = None
		if user:
			logging.info("Fetching profile for %s." % user)
			#user_profile = account_services.getPicture(user.email())
			logging.info(user_profile)
		self.response.out.write(page_template.render({
			'logout_url': users.create_logout_url('/'),
			'login_url': users.create_login_url('/'),
			'user': user_profile}))

class UserProfileHandler(webapp2.RequestHandler):
	def get(self):
		user = users.get_current_user()
		user_profile = account_services.getPicture(user.email())
		template_page = 'profile'
		page_template = JINJA_ENVIRONMENT.get_template('templates/%s.html' % template_page)
		self.response.out.write(page_template.render({'user': user_profile}))

app = webapp2.WSGIApplication([
	webapp2.Route(r'/<page:(academy|courses|dashboard|faq|gallery|library)?>', MainHandler),
	('/invite', InvitationHandler),
	('/addUser', AddUserHandler),
	('/profile', UserProfileHandler)
], debug=True)
