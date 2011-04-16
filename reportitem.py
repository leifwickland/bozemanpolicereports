from google.appengine.ext import db
from google.appengine.ext import webapp
import httplib
import urllib

class ReportItem(db.Model):
    createdTime = db.DateTimeProperty(auto_now_add=True)
    content = db.StringProperty(multiline=True)
    def exists(self):
        return 1 == ReportItem.gql("WHERE content = :1", self.content).count(1)

    def postToTwitter(self):
        params = urllib.urlencode({'status' : self.content[0:120] + " " + "http://bit.ly/JR34s"})
        headers = { 
                'Content-type' : 'application/x-www-form-urlencoded', 
                'Accept' : 'text/plain',
                #'Authorization' : 'Basic %s' % base64.encodestring('bznpolicereport:Bozeman1864')[:-1],
                'Authorization' : 'Basic YnpucG9saWNlcmVwb3J0OkJvemVtYW4xODY0',
                }
        conn = httplib.HTTPConnection('twitter.com');
        conn.request('POST', '/statuses/update.xml', params, headers)
        return conn.getresponse()
