Ensure to have a copy of the python GAE SDK downloaded.
Start the dev server with `google_appengine/dev_appserver.py --clear_datastore true $(readlink -f path/to/this/dir)`
Test if it is scraping correctly by hitting `curl http://localhost:8080/refresh/`
Test if RSS is being formatted correctly with `curl http://localhost:8080/rss | xmlpp | vim -`
Deploy new code with `google_appengine/appcfg.py update  --oauth2 --noauth_local_webserve $(readlink -f path/to/this/dir)`
