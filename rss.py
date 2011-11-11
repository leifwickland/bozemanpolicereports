from reportitem import ReportItem
import PyRSS2Gen
import pprint
import datetime
from google.appengine.api import memcache
import logging 

logging.getLogger().setLevel(logging.DEBUG)

pp = pprint.PrettyPrinter(indent=4)

rssString = memcache.get("rss")
if rssString is not None:  
    logging.debug("Memcache hit!")
else:
    threshold = (datetime.datetime.utcnow() - datetime.timedelta(days=2.5))
    query = ("where createdTime > DATETIME(%d, %d, %d, %d, %d, %d) order by createdTime desc limit 100" % (threshold.year, threshold.month, threshold.day, threshold.hour, threshold.minute, threshold.second))
    items = ReportItem.gql(query)
    rss = PyRSS2Gen.RSS2(
            title = "Bozeman Police Report",
            link = "http://bozemandailychronicle.com/police_reports/",
            description = "Bozeman Police Report",
            lastBuildDate = datetime.datetime.now(),
            items = [])
    for item in items:
        itemguid = "BPR" + item.createdTime.isoformat()
        rss.items.append(PyRSS2Gen.RSSItem(
            title = itemguid,
            guid = itemguid,
            link = "http://bozemandailychronicle.com/police_reports/",
            description = item.content,
            pubDate = item.createdTime,
            ))
    rssString = rss.to_xml()
    memcache.add("rss", rssString, 24 * 60 * 60)
    logging.debug("Memcache set.")

print "Content-Type: application/xhtml+xml"
print rssString
