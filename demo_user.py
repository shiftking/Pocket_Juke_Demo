import os
import urllib
import operator

from operator import itemgetter
from google.appengine.api import users
from google.appengine.ext import ndb

import webapp2
import jinja2


JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

#DEFAULT_PARTY_NAME = 'default_party'


#def party_key(default_party=DEFAULT_PARTY_NAME):
  # """Constructs a Datastore key for a Party entity.
  # We use partyname as the key.

  # """
   #return ndb.Key('partyname', partyname)







class Party(ndb.Model):
    """main model to represent a party"""
    party_name = ndb.StringProperty(indexed=False)
    code = ndb.StringProperty(indexed=False)
    attending = ndb.IntegerProperty()

class User(ndb.Model):
    """Sub Model representing the user"""

    user_id = ndb.StringProperty()
    party_key_id = ndb.StringProperty()

class Song(ndb.Model):
    """main model to represent a song and its parameters"""
    title = ndb.StringProperty()
#   artist = ndb.StringProperty(indexed=False)

    user_suggest = ndb.StringProperty()
    party_id = ndb.StringProperty()
#    song_uli = ndb.StringProperty()
class Activity(ndb.Model):
    """Main model to represent a Activity entry for a Party"""
    song_id = ndb.StringProperty()
    party_id = ndb.StringProperty()
    date = ndb.DateTimeProperty(auto_now_add=True)
    song_name = ndb.StringProperty()


class MainPage(webapp2.RequestHandler):
    def get(self):


            user = users.get_current_user()

            if user:
                #checks to see if the user has been entered into the datastore before
                q = ndb.gql("SELECT * FROM User WHERE user_id = :1",user.user_id())
                res = q.get()

                #self.response.out.write(res)
                if res == None:
                    #self.response.out.write("Could not find user, adding them to datastore")
                    new_user = User(user_id=user.user_id())
                    new_user.put()

                else:
                    if res.party_key_id:
                        self.redirect('/party')

                url = users.create_logout_url(self.request.uri)
                url_linktext = 'Logout'

                template = JINJA_ENVIRONMENT.get_template('templates/index.html')

            else:
                url = users.create_login_url(self.request.uri)

                url_linktext = 'Login'
                template = JINJA_ENVIRONMENT.get_template('templates/login.html')


            template_values = {

                'url': url,
                'url_linktext': url_linktext,
            }
            self.response.write(template.render(template_values))
    def post(self):
        user = User(email=users.get_current_user().email())
        self.redirect('/')

class Start(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()

        if user:
            template = JINJA_ENVIRONMENT.get_template('templates/start.html')
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
        else:
            url = users.create_login_url(self.request.uri)

            url_linktext = 'Login'
            template = JINJA_ENVIRONMENT.get_template('templates/login.html')

        template_values = {

            'url': url,
            'url_linktext': url_linktext,
        }
        self.response.write(template.render(template_values))
    def post(self):
        user = users.get_current_user()

        if user and self.request.get('party_name') !=  "":
            q = ndb.gql("SELECT * FROM User WHERE user_id = :1",user.user_id())
            res = q.get()
            new_party = Party(party_name=self.request.get('party_name'),
                            code=self.request.get('party_code'),
                            )

            party_key = new_party.put()
            res.party_key_id = str(party_key.id())

            res.put()

            self.redirect('/')
        else:
            self.redirect('/')
            url = users.create_login_url(self.request.uri)

            url_linktext = 'Login'

            template = JINJA_ENVIRONMENT.get_template('templates/login.html')



class Join(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()

        if user:

            res = Party.query()

            template = JINJA_ENVIRONMENT.get_template('templates/join.html')
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
            #self.response.out.write(res)
            template_values = {

                'url': url,
                'url_linktext': url_linktext,
                'party_list': res,
            }
            self.response.write(template.render(template_values))
        else:
            url = users.create_login_url(self.request.uri)

            url_linktext = 'Login'
            template = JINJA_ENVIRONMENT.get_template('templates/login.html')
            template_values = {

                'url': url,
                'url_linktext': url_linktext,

            }
            self.response.write(template.render(template_values))
    def post(self):
        user =  users.get_current_user()
        party_name = self.request.get('party_id')

        q = ndb.gql("SELECT * FROM User WHERE user_id = :1",user.user_id())
        res = q.get()
        res.party_key_id = str(party_name)
        res.put()

        self.redirect('/party')





class ActiveParty(webapp2.RequestHandler):
    def get(self):

        user = users.get_current_user()

        if user:
            template = JINJA_ENVIRONMENT.get_template('templates/party.html')
            q = ndb.gql("SELECT * FROM User WHERE user_id = :1",user.user_id())
            res = q.get()

            party_id = ndb.Key(urlsafe=res.party_key_id)
            party_res = party_id.get()

            #we need to get all of the activities so we can build the queue
            #we dont need to sort the response, because the response is sorted already
            res2 = Activity.query(Activity.party_id == res.party_key_id).order(Activity.song_name,Activity.date)
            #set up our constant values
            #One of them is the maximum time between votes to be considered consecutive
            max_time_apart = 5 #this is in seconds

            #this one is for the time frame before the end of the current song
            max_before_start = 2000 #this is in miliseconds
            #this is the threshold minimum number of consecutive songs
            min_consect_songs = 3
            #variable to keep track of the total number of consecutive songs
            consect_songs = 0
            #for the consecutive songs the buff is .1 %
            consect_buff = 1.001
            #buff for a standard vote
            vote_buff = 1.0005
            #for the before the end of the current song buff its .5%
            before_buff = 1.005


            queue = []

            pre_entry = None
            def close_time(date1,date2):
                if(date1.year == date2.year):
                    if(date1.month == date2.month):
                        if(date1.day == date2.day):
                            if(date1.hour == date2.hour):
                                if(date1.minute == date2.minute):
                                    if(date1.second - date2.second < 5):
                                        return True
                return False


            for entry in res2:
                if not any(d['song_name'] == entry.song_name for d in queue):
                    consect_songs = 0

                    song_pos = {
                        'song_name' : entry.song_name,
                        'weight' : 1,
                        'song_id': entry.song_id,
                    }
                    queue.append(song_pos)
                    pre_entry = entry
                else:
                    pos = map(itemgetter('song_name'),queue).index(entry.song_name)


                    if consect_songs > min_consect_songs:
                        weight = queue[pos]['weight']
                        queue[pos]["weight"]  = weight * consect_buff
                    else:
                        weight = queue[pos]['weight']
                        queue[pos]["weight"]  = weight * vote_buff
                    if close_time(pre_entry.date,entry.date):
                              consect_songs += 1
                    else:
                              consect_songs = 0
                    #will add this back later
                    #if entry.date.seconds() - 500000 < max_before_start:
                    #          queue[pos]['weight'] *= before_buff
                    pre_entry = entry

            sorted_queue = sorted(queue, key=operator.itemgetter('weight'),reverse=True)
            for item in sorted_queue:
                self.response.out.write(item['weight'])

            template_values={
                'queue': sorted_queue,
                'party_name': party_res.party_name
            }

            self.response.write(template.render(template_values))
        else:
            url = users.create_login_url(self.request.uri)

            url_linktext = 'Login'
            template = JINJA_ENVIRONMENT.get_template('templates/login.html')
            template_values = {

                'url': url,
                'url_linktext': url_linktext,

            }
            self.response.write(template.render(template_values))


        #self.response.out.write("Hello")
    def post(self):
        response = self.request.get("vote")
        if response == "true":

            user = users.get_current_user()

            if user:
                songID = self.request.get("song_id")
                query_song_key = ndb.Key(urlsafe=songID)
                song = query_song_key.get()

                party_key = song.party_id
                #party = party_key.get()
                entry = Activity(party_id=party_key,
                                song_id=songID,
                                song_name=song.title)
                entry.put()
                self.redirect('/party')


            else:
                url = users.create_login_url(self.request.uri)

                url_linktext = 'Login'
                template = JINJA_ENVIRONMENT.get_template('templates/login.html')
                template_values = {

                    'url': url,
                    'url_linktext': url_linktext,

                }
                self.response.write(template.render(template_values))
        else:
            user = users.get_current_user()
            if user:
                q = ndb.gql("SELECT * FROM User WHERE user_id = :1",user.user_id())
                res = q.get()
                party_key = res.party_key_id
                name = self.request.get("song_name")
                #see if the song has already been added

                res2 = Song.query(Song.title == name)
                #q2 = ndb.gql("SELECT * FROM Song WHERE title = :1",name)
                #res2 = q2.get()

                #if res2 == None:
                for ent in res2:
                    if ent.title == name:
                        self.redirect('/party')

                song = Song(title=name,user_suggest=user.user_id(),
                            party_id=str(party_key)

                            )
                songID = song.put()
                activity = Activity(party_id=party_key,
                                    song_id=songID.urlsafe(),
                                    song_name=name
                                    )
                activity.put()



                self.redirect('/')









            else:
                url = users.create_login_url(self.request.uri)

                url_linktext = 'Login'
                template = JINJA_ENVIRONMENT.get_template('templates/login.html')
                template_values = {

                    'url': url,
                    'url_linktext': url_linktext,

                }
                self.response.write(template.render(template_values))

app = webapp2.WSGIApplication([
        ('/', MainPage),
        ('/start', Start),
        ('/join', Join),
        ('/party', ActiveParty),
], debug=True)
