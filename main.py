
import os
import webapp2
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                                autoescape = True)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        page = jinja_env.get_template(template)
        return page.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class Notepad(db.Model):
    title = db.StringProperty(required = True)
    entry = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

class HomePage(Handler):

    def get(self):

        entries = db.GqlQuery("SELECT * FROM Notepad ORDER BY created DESC")
        self.render("home.html", entries=entries)

class AddEntry(Handler):
    def render_newpost(self, title="", entry="", error=""):

        self.render("newpost.html", title=title, entry=entry, error=error)

    def get(self):
        self.render_newpost()

    def post(self, title="", entry="", error=""):
        title = self.request.get("title")
        entry = self.request.get("entry")

        if title and entry:
            newEntry = Notepad(title = title, entry=entry)
            newEntry.put()
            self.redirect("/" + str(newEntry.key().id()))

            #self.redirect("/")
        else:
            error = "we need both a title and some awesomeness!"
            self.render_newpost(title, entry, error)


class ViewPostHandler(Handler):
    def get(self, entry_id):
        entry_id = Notepad.get_by_id(int(entry_id))

        if entry_id:
            self.render("oldpost.html", entry_id=entry_id)
        else:
            self.respose.write("You can't mess with awesome")


app = webapp2.WSGIApplication([
    ('/', HomePage),
    ('/add', AddEntry),
    webapp2.Route('/<entry_id:\d+>', ViewPostHandler)
    ], debug=True)
