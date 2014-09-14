#!/usr/bin/env python
import os
import logging
from google.appengine.api import mail
import webapp2
import jinja2
if os.environ['SERVER_SOFTWARE'].startswith('Development'):
	import account_services_dev as govlab
else:
	import account_services as govlab
from google.appengine.api import users

from model import UserProfile
from model import UserProject
from model import ProjectCanvas

import json

USER_MAPPING = govlab.getUserMapping()

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)
JINJA_ENVIRONMENT.filters['id2name'] = lambda x: USER_MAPPING.setdefault(x+'@thegovlab.org', x)

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
			user_profile = govlab.getUserProfile(user.email())
			logging.info(user_profile)
		self.response.out.write(page_template.render({
			'logout_url': users.create_logout_url('/'),
			'login_url': users.create_login_url('/'),
			'user': user_profile,
			'me': user_profile }))

class UserProfileHandler(webapp2.RequestHandler):
	def get(self):
		logging.info("inside GET")
		user = users.get_current_user()
		user_id = user.email()
		me = govlab.getUserProfile(user.email())
		# Checking someone else's profile
		readonly = False
		if self.request.get('user_email'):
			user_id = self.request.get('user_email')
			logging.info("Showing readonly profile for user %s." % user_id)
			readonly = True
		user_profile = UserProfile.get_by_id(user_id)
		logging.info(user_profile)
		user_profile_govlab = govlab.getUserProfile(user_id)
		logging.info(user_profile_govlab)
		if user_profile_govlab == None:
			self.abort(404)
		user_profile_json = {}
		if user_profile and user_profile.profile:
			user_profile_json = json.loads(user_profile.profile)
		user_profile_json['user'] = user_profile_govlab
		user_profile_json['readonly'] = readonly
		user_profile_json['user_id'] = user_id
		user_profile_json['me'] = me
		template_page = 'profile'
		page_template = JINJA_ENVIRONMENT.get_template('templates/%s.html' % template_page)
		self.response.out.write(page_template.render(user_profile_json))

	def post(self):
		logging.info("inside POST")
		user = users.get_current_user()
		user_profile_json = {
		'fname': self.request.get('fname'),
		'lname': self.request.get('lname'),
		'city_state': self.request.get('city_state'),
		'country': self.request.get('country'),
		'facebook': self.request.get('facebook'),
		'twitter': self.request.get('twitter'),
		'github': self.request.get('github'),
		'linkedin': self.request.get('linkedin'),
		'year_experience': self.request.get('year_experience'),
		'sector_experience': self.request.get('sector_experience'),
		'expertise': self.request.get('expertise'),
		'experience': self.request.get('experience'),
		'offer': self.request.get('offer'),
		'demand': self.request.get('demand')
		}
		user_profile = UserProfile(id=user.email(), profile=json.dumps(user_profile_json))
		user_profile.put()
		logging.info('profile stored')
		self.redirect('/profile')

class AllProjectsHandler(webapp2.RequestHandler):
	def get(self):
		user = users.get_current_user()
		me = govlab.getUserProfile(user.email())
		page_template = JINJA_ENVIRONMENT.get_template('templates/all_projects.html')
		projects = UserProject.query().fetch(100)
		self.response.out.write(page_template.render({
			'projects': projects,
			'me': me }))

class ProjectHandler(webapp2.RequestHandler):
	def get(self, project_id):
		USER_MAPPING = govlab.getUserMapping()
		logging.info("User Mapping:")
		logging.info(USER_MAPPING)
		user = users.get_current_user()
		me = govlab.getUserProfile(user.email())
		project = UserProject.get_by_id(project_id)
		if project == None:
			self.abort(404)
		readonly = True
		logging.info("Checking ACL")
		logging.info(user.email().split('@')[0] in project.members)
		if user.email().split('@')[0] in project.members:
			readonly = False
		if users.is_current_user_admin():
			readonly = False
		logging.info("readonly: %s" % readonly)
		page_template = JINJA_ENVIRONMENT.get_template('templates/project.html')
		members = [ { 'id': k+'@thegovlab.org', 'fullName': USER_MAPPING[k+'@thegovlab.org'] } for k in project.members]
		logging.info(members)
		self.response.out.write(page_template.render({
			'project': project,
			'readonly': readonly,
			'members': members,
			'me': me }))

	def post(self, project_id):
		user = users.get_current_user()
		me = govlab.getUserProfile(user.email())
		project = UserProject.get_by_id(project_id)
		if project == None:
			logging.error("Not a valid project.")
			self.abort(404)
		if (user.email().split('@')[0] not in project.members) and (users.is_current_user_admin() == False):
			logging.error("Only project team or admin can update a project.")
			self.abort(404)
		project_title = self.request.get('title')
		project_description = self.request.get('description')
		project.title = project_title
		project.description = project_description
		project.blogURL = self.request.get('blogURL')
		project.put()
		self.redirect('/project/%s' % project.shortName)

class CanvasHandler(webapp2.RequestHandler):
	def get(self):
		user = users.get_current_user()
		me = govlab.getUserProfile(user.email())
		canvas = ProjectCanvas.get_by_id(user.email())
		logging.info(canvas)
		page_template = JINJA_ENVIRONMENT.get_template('templates/canvas.html')
		canvas_data = {}
		if canvas:
			canvas_data = json.loads(canvas.content)
		self.response.out.write(page_template.render({'me': me, 'canvas': canvas_data}))

	def post(self):
		user = users.get_current_user()
		me = govlab.getUserProfile(user.email())
		canvas = ProjectCanvas.get_by_id(user.email())
		canvas_content = {}
		for field in ProjectCanvas.getFields(): # we extract all the fields from the form.
			canvas_content[field] = self.request.get(field)
		if canvas:
			canvas.content = json.dumps(canvas_content)
		else:
			canvas = ProjectCanvas(id=user.email(), content=json.dumps(canvas_content))
		canvas.put()
		self.redirect('/canvas')

app = webapp2.WSGIApplication([
	webapp2.Route(r'/<page:(academy|courses|dashboard|faq|gallery|library)?>', MainHandler),
#	('/invite', InvitationHandler),
#	('/addUser', AddUserHandler),
	('/profile', UserProfileHandler),
	('/project/([a-z0-9_-]+)', ProjectHandler),
	('/projects', AllProjectsHandler),
	('/canvas', CanvasHandler),
], debug=True)
