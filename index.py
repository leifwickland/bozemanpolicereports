# coding=utf-8
import logging
import httplib
import re
from reportitem import ReportItem
import htmlentitydefs
import os
from google.appengine.api import memcache

def getPage():
    url = ''
    if '/refresh/' == os.getenv('PATH_INFO')[0:9]:
        logging.debug("Got a different URL in request")
        url = os.getenv('PATH_INFO')[8:1000]
    if len(url) < 3:
        url = "/police_reports/"
        logging.debug("Using standard URL")
    logging.debug("URL: %s" % url)
    conn = httplib.HTTPConnection("www.bozemandailychronicle.com")
    conn.request("GET", url)
    r = conn.getresponse()
    return unicode(r.read(), "utf-8")

def parseBodyFromPage(page):
    state = "lookingForStory"
    lines = page.splitlines()
    body = ''
    for line in lines:
        debugAndPrint("State = " + state + "    line = " + line)
        if state == "lookingForStory":
            if line.find("storytext") >= 0:
                state = "lookingForEndOfStory"
        elif state == "lookingForEndOfStory":
            if (line.find('tncms-region-center-three-index') >= 0) or (line.find('blox-top-right') >= 0):
                debugAndPrint("Found end of body marker.")
                state = "DoneWithBody"
                break
            body += (line.strip() + " ")
    debugAndPrint("Body: %s" % body)
    return body

def parseItemsFromBody(body):
    items = []
    for item in re.findall('<(?:li)[^>]*>(?:<[^>]+>)*(.+?)(?:<[^>]+>)*</(?:li)>', body):
        debugAndPrint("Raw item: " + item);
        item = re.sub('<[^>]+>', '', item)
        item = re.sub('“|”', '"', item)
        item = re.sub('’', "'", item)
        item = re.sub(u" ", " " , item)
        
        item = item.strip()
        debugAndPrint("Fixed up item: " + item);
        if len(item) == 0:
            continue
        if 0 <= item.find('index-story-prologue'):
            continue
        if 0 <= item.find('included the following'):
            continue
        if re.search('\d+\s+(inmates|people under its supervision)', item):
            continue
        if re.search('people.*sheriff.*county work program', item):
            continue
        if item == 'Advertisement':
            continue
        items.append(item)
        logging.debug("Item: %s" % item)
    return items

# I wanted to remove entites because they took up extra space in the short message.
# The problem was that the original code converted some of them to unicode
# characters which made various other parts of the system angry.
# Stolen from http://www.w3.org/QA/2008/04/unescape-html-entities-python.html
def unescape(text):
    def fixup(m):
        text = m.group(0)
        if text[:2] == "&#":
            if text[:3] == "&#x":
                val = int(text[3:-1], 16)
            else:
                val = int(text[2:-1])
            if val > 128:
                return ''
            return unichr(val)
        if text[1:-1] == "amp":
            return '&'
        if text[1:-1] == "gt":
            return '>'
        if text[1:-1] == "lt":
            return '<'
        if text[1:-1] == "quot":
            return '"'
        if text[1:-1] == "rsquo":
            return "'"
        if text[1:-1] == "lsquo":
            return "'"
        if text[1:-1] == "rdquo":
            return '"'
        if text[1:-1] == "ldquo":
            return '"'
        return ''

    return re.sub("&#?\w+;", fixup, text)

def createReportItemsFromNewItems(items):
    reportItems = []
    for item in items:
        reportItem = ReportItem()
        reportItem.content = unescape(item)[0:499] #The max size for the GQL string type is 500 characters
        if reportItem.exists():
            continue
        reportItems.append(reportItem)
    return reportItems

def debugAndPrint(message):
    message = unicode(message).encode('ascii', 'replace');
    print message
    logging.debug(message)

def errorAndPrint(message):
    print message
    logging.error(message)


print 'Content-type: text/plain; charset=utf-8'
print ''
print 'Starting to look for new items...' 
newItems = createReportItemsFromNewItems(parseItemsFromBody(parseBodyFromPage(getPage())))
if len(newItems) == 0:
    debugAndPrint("There's nothing new under the sun.")
else:
    debugAndPrint("Starting to post items: %d" % len(newItems))
    for newItem in newItems:
        newItem.put()
        debugAndPrint('Successfully recorded: ' + newItem.content)
    memcache.delete("rss")
    debugAndPrint("Invalidated memcache")
