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

from domain_services import *

class MainHandler(webapp2.RequestHandler):
	def get(self, page):
		user = users.get_current_user()
		template_page = page
		if page is None or page == "":
			if user and validUser(user.email()):
				template_page = 'dashboard'
			else:
				template_page = 'academy'
		page_template = get_template('templates/%s.html' % template_page)
		user_profile = None
		if user:
			user_profile = getUserProfile(user.email())
		self.response.out.write(page_template.render({
			'logout_url': users.create_logout_url('/'),
			'login_url': users.create_login_url('/'),
			'me': user_profile }))

class UserProfileHandler(webapp2.RequestHandler):
	def get(self):
		user = users.get_current_user()
		my_profile = getUserProfile(user.email())
		user_profile = my_profile
		readonly = False

		# Checking someone else's profile?
		if self.request.get('user_email'):
			profile_email = self.request.get('user_email')
			user_profile = getUserProfile(profile_email)
			readonly = True
			if user_profile == None:
				self.abort(404)

		template_data = {}
		if user_profile and user_profile.profile:
			template_data = json.loads(user_profile.profile)
		template_data['lname'] = user_profile.lname
		template_data['fname'] = user_profile.fname
		template_data['photoUrl'] = user_profile.photoUrl
		template_data['affiliation'] = user_profile.affiliation
		template_data['me'] = my_profile
		template_data['readonly'] = readonly
		page_template = get_template('templates/profile.html')
		self.response.out.write(page_template.render(template_data))

	def post(self):
		"""We only update the profile part of the profile."""
		user = users.get_current_user()
		user_profile = UserProfile.get_by_id(user.email())
		if user_profile is None:
			self.abort(404)
		user_profile_json = {}
		for field in UserProfile.getFields():
			user_profile_json[field] = self.request.get(field)
		user_profile.profile = json.dumps(user_profile_json)
		user_profile.put()
		logging.info('profile stored')
		self.redirect('/profile')

class AllProjectsHandler(webapp2.RequestHandler):
	def get(self):
		user = users.get_current_user()
		me = getUserProfile(user.email())
		page_template = get_template('templates/all_projects.html')
		projects = UserProject.query().fetch(100)
		self.response.out.write(page_template.render({
			'projects': projects,
			'me': me }))

class ProjectHandler(webapp2.RequestHandler):
	def get(self, project_id):
		USER_MAPPING = getUsersMapping()
		user = users.get_current_user()
		me = getUserProfile(user.email())
		project = UserProject.get_by_id(project_id)
		if project == None:
			self.abort(404)
		readonly = True

		if userCanEditProject(user.email(), project):
			readonly = False
		members = project.members
		page_template = get_template('templates/project.html')
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
		me = getUserProfile(user.email())
		canvas = ProjectCanvas.get_by_id(user.email())
		canvas_data = {}
		if canvas:
			canvas_data = json.loads(canvas.content)
		page_template = get_template('templates/canvas.html')
		self.response.out.write(page_template.render({'me': me, 'canvas': canvas_data}))

	def post(self):
		user = users.get_current_user()
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

class AllUsersHandler(webapp2.RequestHandler):
	def get(self):
		user = users.get_current_user()
		me = getUserProfile(user.email())
		all_users = {}
		for user in UserProfile.query().order(UserProfile.lname, UserProfile.fname).fetch(limit=500):
			all_users.setdefault(user.affiliation, []).append(user)

		sortStudents = lambda x:x['name']['familyName']
		template_values = {
		'me': me,
		#TODO (arnaud): sort
		'faculty': all_users.setdefault('GovLab', []),
		'mit_students': all_users.setdefault('MIT', []),
		'nyu_students': all_users.setdefault('NYU', []),
		'online_students': all_users.setdefault('online', []) }
		template = get_template('templates/class_roster.html')
		self.response.out.write(template.render(template_values))

app = webapp2.WSGIApplication([
	webapp2.Route(r'/<page:(academy|courses|dashboard|faq|gallery|library)?>', MainHandler),
#	('/invite', InvitationHandler),
#	('/addUser', AddUserHandler),
	('/profile', UserProfileHandler),
	('/project/([a-z0-9_-]+)', ProjectHandler),
	('/projects', AllProjectsHandler),
	('/canvas', CanvasHandler),
	('/fall-2014-class', AllUsersHandler),
], debug=True)