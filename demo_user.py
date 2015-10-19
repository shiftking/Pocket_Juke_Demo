import os
import urllib

from google.appengine.api import users
from google.appengine.ext import ndb

import webapp2
import jinja2


JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

#DEFAULT_PARTY_NAME = 'default_party'


#def default_party_key(default_party=DEFAULT_DEMO_USER_NAME):
#    """Constructs a Datastore key for a Party entity.
#    We use partyname as the key.

#    """
#    return ndb.Key('partyname', partyname)


#class User(ndb.Model):
#   """Sub Model representing the user"""
#   party_number = ndb.StructuredProperty(Party)
#   email = ndb.StringProperty(indexed=False)


#class Song(ndb.Model):
#    """main model to represent a song and its parameters"""
#    title = ndb.StringProperty(indexed=False)
#    artist = ndb.StringProperty(indexed=False)
#    song_position = ndb.IntegerProperty()
#    user_sugest = ndb.StringProperty()
#     party_number = ndb.StructuredProperty()
#    song_uli = ndb.StringProperty()

#class Party(ndb.Model):
#   """main model to represent a party"""
#   party = ndb.IntegerProperty()




class MainPage(webapp2.RequestHandler):
    def get(self):
        #self.response.headers['Content-Type'] = 'text/plain'
        #self.response.write('Hello, World!')

        #checks for an active Goolge user account

        user = users.get_current_user()

        if user:



            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
            template = JINJA_ENVIRONMENT.get_template('index.html')

        else:
            url = users.create_login_url(self.request.uri)

            url_linktext = 'Login'
            template = JINJA_ENVIRONMENT.get_template('login.html')


        template_values = {

            'url': url,
            'url_linktext': url_linktext,
        }
        self.response.write(template.render(template_values))

class Start(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()

        if user:
            template = JINJA_ENVIRONMENT.get_template('start.html')
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
        else:
            url = users.create_login_url(self.request.uri)

            url_linktext = 'Login'
            template = JINJA_ENVIRONMENT.get_template('login.html')

        template_values = {

            'url': url,
            'url_linktext': url_linktext,
        }
        self.response.write(template.render(template_values))



        #if uses.get_current_user():
        #    party_name = self.request.get('partyname')
        #    party_code = self.request.get('partycode')

        #    party = Party(parent=)

class Join(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()

        if user:
            template = JINJA_ENVIRONMENT.get_template('join.html')
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
        else:
            url = users.create_login_url(self.request.uri)

            url_linktext = 'Login'
            template = JINJA_ENVIRONMENT.get_template('login.html')

        template_values = {

            'url': url,
            'url_linktext': url_linktext,
        }
        self.response.write(template.render(template_values))



app = webapp2.WSGIApplication([
        ('/', MainPage),
        ('/start', Start),
        ('/join', Join),
], debug=True)
