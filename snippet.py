from google.appengine.api import users
from google.appengine.ext import ndb
from datetime import datetime
from datetime import timedelta

import os
import logging
import jinja2
import webapp2
from model import UserSnippet

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

class SnippetHandler(webapp2.RequestHandler):
    SNIPPET_START_DATE = datetime(2014, 1, 1) # First Wed of 2014 

    @staticmethod
    def weekRange(week):
        """For a given week, returns the start and end date as human friendly strings.
           e.g. 29 => `23, Jul 2014 (Wednesday) and 29, Jul 2014 (Tuesday)`
        """
        start_date = SnippetHandler.SNIPPET_START_DATE + timedelta(days=7*week)
        end_date   = SnippetHandler.SNIPPET_START_DATE + timedelta(days=7*(week+1)-1)
        return {"start": "{:%d, %b %Y (%a)}".format(start_date),
                "end": "{:%d, %b %Y (%a)}".format(end_date) }

    def get(self, _user=None, _week=None):
        logging.info("_user = %s, _week=%s" % (_user, _week))
        logging.info("Current user: " + users.get_current_user().email())
        
        (user_id, domain) = users.get_current_user().email().split('@')
        current_week = (datetime.today() - SnippetHandler.SNIPPET_START_DATE).days / 7
        isEmbed = self.request.get("embedded", default_value="false")

        """We handle various default options using redirect.
           - default user = logged in user.
           - default week = this week.
        """
        if _user == None:
            self.redirect('/snippet/%s?embedded=%s' % (user_id, isEmbed))
            return
        if _week == None:
            self.redirect('/snippet/%s/%d?embedded=%s' % (_user, current_week, isEmbed))
            return

        # Starting from here, both `_user` and `_week` are properly assigned.
        user = _user
        week = int(_week)
        
        edit = False
        if _user == user_id:
            edit = True
        
        # We get the snippet from the database if any.
        snippet = UserSnippet.get_by_id(id=week, parent=ndb.Key("User", user))
        if snippet:
            snippet_data = snippet.content
        else:
            snippet_data = "N/A"

            
        template = JINJA_ENVIRONMENT.get_template('templates/snippet.html')
        template_values = {
            'username': user,
            'domain': domain,
            'start_date': SnippetHandler.weekRange(week)['start'],
            'end_date': SnippetHandler.weekRange(week)['end'],
            'snippet_content': snippet_data,
            'week': week,
            'prev_week': week-1,
            'next_week': week+1,
            'edit': edit,
            'embedded': isEmbed
        }
        self.response.out.write(template.render(template_values))

    def post(self, user, week):
        logging.info("Inside POST")
        (user_id, domain) = users.get_current_user().email().split('@')
        isEmbed = self.request.get("embedded", default_value="false")
        # Only a user can update her snippet.
        if user != user_id:
            self.abort(403)

        snippet_data = self.request.get('snippet_data')
        snippet = UserSnippet(parent=ndb.Key("User", user), id=int(week), content=snippet_data)
        snippet.put()
        self.redirect('/snippet/%s/%s?embedded=%s' % (user, week, isEmbed))

class MainHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write("default route")

app = webapp2.WSGIApplication([
    (r'/snippet/(.+)/(.+)', SnippetHandler),
    (r'/snippet/(.+)', SnippetHandler),
    (r'/snippet/', SnippetHandler),
    ], debug=True)
