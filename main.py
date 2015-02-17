import os
import jinja2
import webapp2
from google.appengine.api import users
from google.appengine.ext import ndb

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


class Person(ndb.Model):
    identity = ndb.StringProperty(indexed=False)
    email = ndb.StringProperty(indexed=False)


class Contact(ndb.Model):
    friend = ndb.StructuredProperty(Person)
    name = ndb.StringProperty(required=True)
    gender = ndb.StringProperty(indexed=False)
    mobileos = ndb.StringProperty(repeated=True)
    browser = ndb.StringProperty(indexed=False)
    remark = ndb.StringProperty(indexed=False)
    date = ndb.DateTimeProperty(auto_now_add=True)


class MainPage(webapp2.RequestHandler):
    def get(self):
        contact_query = Contact.query().order(-Contact.date)
        contacts = contact_query.fetch(10)

        user = users.get_current_user()
        if user:
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'

        template_values = {
            'user': user,
            'contacts': contacts,
            'url': url,
            'url_linktext': url_linktext,
        }

        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render(template_values))


class AddPage(webapp2.RequestHandler):
    def post(self):
        contact = Contact()

        if users.get_current_user():
            contact.friend = Person(
                    identity=users.get_current_user().user_id(),
                    email=users.get_current_user().email())
        contact.name = self.request.get('cname')
        contact.gender = self.request.get('cgender')
        contact.mobileos = list(self.request.get_all('cmobileos'))
        contact.browser = self.request.get('cbrowser')
        contact.remark = self.request.get('cremark')
        contact.put() # commit change

        self.redirect('/')


app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/add', AddPage),
], debug=True)