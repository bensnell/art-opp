import os
import sys
import requests
from tinydb import TinyDB, Query
import re
import time
from datetime import datetime
from feedgen.feed import FeedGenerator
from git import Repo

# Get the current working directory
def getWorkingDir():
	return os.path.dirname(os.path.abspath(__file__))

def getTimestampString():
	return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# TODO: Make sure there is a feeds directory

# ========== USERPARAMS ============

# Url to get the listings
listingsURL = "https://www.nyfa.org/Opportunities/Search"

# Create a database if one doesn't exist
db = TinyDB(getWorkingDir() + "/" + "db.json")

# Number of seconds to refresh
refreshSec = 60*60 # every hr

# Number of last seconds of data to include in every feed file
includeSec = 60 * 60 * 24

githubRepoURL = "https://raw.githubusercontent.com/bensnell/art-opp/master/"
repoName = "art-opp"

# =========== CODE =============

saveFolderPath = getWorkingDir() + "/" + "feeds"
if not os.path.exists(saveFolderPath):
	os.makedirs(saveFolderPath)

# Try to get the url of the listings
def getListings(URL, pageNumber):
	data = None
	try:
		# Reference: https://apitester.com/
		payload = {"pageNumber" : pageNumber}
		response = requests.post(URL, data = payload)
		data = response.json()["Regular_Listings"]
		if len(data) == 0:
			data = None
	except:
		print("Could not retrieve the url " + URL)
		data = None
	return data

def uniqueListOfDicts(tag, array):
	return list({v[tag]:v for v in array}.values())

def getAllListings(URL, maxPages):

	out = []
	for i in range(1, maxPages+1):
		pagelistings = getListings(URL, i)
		if pagelistings == None:
			break
		out = out + pagelistings
	return uniqueListOfDicts("ID", out)

# Parse the information for opportunities; returns a list of ID's
def parseListings(listings, types):
	out = []
	# Find all of the specified type(s)
	for item in listings:
		thisID = ""
		try:
			thisID = item["ID"]
			if item["OppType"] in types:
				out.append(thisID)
		except:
			print("Error while parsing type in post with ID " + thisID)
	return out

# Compare these IDs with those in our database to determine which are new
def getNewListings(ids):
	out = []
	Q = Query()
	for thisID in ids:
		try:
			searchResults = db.search(Q.ID == thisID)
			if len(searchResults) == 0:
				# This is a new post
				out.append(thisID);
				# Don't add to db yet
		except:
			print("Error while searching db for ID " + ID)
	return out

# Get the html text from a listing
def getListingHTMLText(url):
	out = None
	try:
		response = requests.get(url)
		out = response.text
	except:
		print("Could not get text from url " + url)
		out = None
	return out

def getTitle(opp, text):
	try:
		obj = re.search( r'<p class=\"contentTitle contentTitleMarginTop\">\s*(.*?)\s*</p>', text, re.M|re.I|re.S)
		opp["Title"] = obj.group(1).strip().replace("&#13;","<br/>")
	except:
		print("Could not retrieve title information for "+opp["ID"])
		print(text)
		opp["Title"] = " "
		return False
	return True

def getOrganization(opp, text):
	try:
		obj = re.search( r'Organization</div><div class=\"info-right-column mobile-width-100-center\">\s*(.*?)\s*</div>', text, re.M|re.I|re.S)
		opp["Organization"] = obj.group(1).strip().replace("&#13;","<br/>")
	except:
		print("Could not retrieve organization information for "+opp["ID"])
		opp["Organization"] = " "
		return False
	return True

def getWebsite(opp, text):
	try:
		obj = re.search( r'Website</div><div class=\"info-right-column mobile-width-100-center\">\s*<a href=\"\s*(.*?)\s*\" target=\"_blank\"', text, re.M|re.I|re.S)
		opp["Website"] = obj.group(1).strip().replace("&#13;","<br/>")
	except:
		print("Could not retrieve website information for "+opp["ID"])
		opp["Website"] = " "
		return False
	return True

def getCountry(opp, text):
	try:
		obj = re.search( r'Country</div><div class=\"info-right-column mobile-width-100-center\">\s*(.*?)\s*</div>', text, re.M|re.I|re.S)
		opp["Country"] = obj.group(1).strip().replace("&#13;","<br/>")
	except:
		print("Could not retrieve country information for "+opp["ID"])
		opp["Country"] = " "
		return False
	return True

def getLocation(opp, text):
	try:
		obj = re.search( r'Location</div><div class=\"info-right-column mobile-width-100-center\">\s*(.*?)\s*</div>', text, re.M|re.I|re.S)
		opp["Location"] = obj.group(1).strip().replace("&#13;","<br/>")
	except:
		print("Could not retrieve location information for "+opp["ID"])
		opp["Location"] = " "
		return False
	return True

def getOpportunityType(opp, text):
	try:
		obj = re.search( r'Opportunity Type</div><div class=\"info-right-column mobile-width-100-center\">\s*(.*?)\s*</div>', text, re.M|re.I|re.S)
		opp["Opportunity Type"] = obj.group(1).strip().replace("&#13;","<br/>")
	except:
		print("Could not retrieve opportunity type information for "+opp["ID"])
		opp["Opportunity Type"] = " "
		return False
	return True

def getOpportunityDiscipline(opp, text):
	try:
		obj = re.search( r'Opportunity Discipline</div><div class=\"info-right-column mobile-width-100-center\">\s*(.*?)\s*</div>', text, re.M|re.I|re.S)
		opp["Opportunity Discipline"] = obj.group(1).strip().replace("&#13;","<br/>")
	except:
		print("Could not retrieve opportunity discipline information for "+opp["ID"])
		opp["Opportunity Discipline"] = " "
		return False
	return True

def getApplicationFee(opp, text):
	try:
		obj = re.search( r'Application Fee</div><div class=\"info-right-column mobile-width-100-center\">\s*(.*?)\s*</div>', text, re.M|re.I|re.S)
		opp["Application Fee"] = obj.group(1).strip().replace("&#13;","<br/>")
	except:
		print("Could not retrieve application fee information for "+opp["ID"])
		opp["Application Fee"] = " "
		return False
	return True

def getApplicationDeadline(opp, text):
	try:
		obj = re.search( r'Application Deadline</div><div class=\"info-right-column mobile-width-100-center\">\s*(.*?)\s*</div>', text, re.M|re.I|re.S)
		opp["Application Deadline"] = obj.group(1).strip().replace("&#13;","<br/>")
	except:
		print("Could not retrieve application deadline information for "+opp["ID"])
		opp["Application Deadline"] = " "
		return False
	return True

# Issue: https://stackoverflow.com/questions/20056306/match-linebreaks-n-or-r-n
def getDescription(opp, text):
	try:
		obj = re.search( r'Description</h2>\s*<div class=\"projectDetailsDiv text-justify text-pre-wrap\">\s*(.*?)\s*</div>', text, re.M|re.I|re.S)
		opp["Description"] = obj.group(1).strip().replace("&#13;","<br/>")
	except:
		print("Could not retrieve description information for "+opp["ID"])
		opp["Description"] = " "
		return False
	return True

def getApplicationInstructions(opp, text):
	try:
		obj = re.search( r'Application Instructions / Public Contact Information</h2>\s*<div class=\"projectDetailsDiv text-justify text-pre-wrap\">\s*(.*?)\s*</div>', text, re.M|re.I|re.S)
		opp["Application Instructions"] = obj.group(1).strip().replace("&#13;","<br/>")
	except:
		print("Could not retrieve application instructions information for "+opp["ID"])
		opp["Application Instructions"] = " "
		return False
	return True

# Return a dictionary with attributes describing this listing
# If we couldn't retrieve information, None is returned
def getListingAttributes(ID):

	# Get this url
	thisUrl = "https://www.nyfa.org/Opportunities/Show/"+ID
	# Retrieve the page
	text = getListingHTMLText(thisUrl)
	if (text == None): return None

	# Output dictionary with attributes
	out = {}
	out["ID"] = ID
	out["url"] = thisUrl; # url of post
	getTitle(out, text)
	getOrganization(out, text)
	getWebsite(out, text)
	getCountry(out, text)
	getLocation(out, text)
	getOpportunityType(out, text)
	getOpportunityDiscipline(out, text)
	getApplicationFee(out, text)
	getApplicationDeadline(out, text)
	getApplicationInstructions(out, text)
	getDescription(out, text)
	# Set the time we retrieved this data
	out["timestamp"] = getTimestampString();

	return out

# Get all listing attributes for a group of IDs
def getAllListingsAttributes(ids):

	out = []
	for ID in ids:

		# Get this object from the id
		thisObject = getListingAttributes(ID)
		if thisObject != None:
			# Save this object
			out.append(thisObject)
	return out

# Add all of the new opportunities to the RSS feed
def saveToDB(_db, array):
	for item in array:
		_db.insert(item)

# Get all items within a timeframe
def getLastItems(_db, _lastSec):

	out = []
	for item in _db:

		if "ID" not in item:
			continue

		# Get this item's time
		itemTime = datetime.strptime(item["timestamp"], '%Y-%m-%d %H:%M:%S')

		# Check if this time is long ago enough
		dt = datetime.now() - itemTime
		diff = dt.total_seconds()
		if diff < _lastSec:
			out.append(item)

	return out

# Format a post for the rss feed
def getHtmlFormattedListing(post):

	out = ""

	# out = out + "<p>" + post["Title"] + "</p>"
	out = out + "<p>" + post["Organization"] + "<br/>"
	out = out + "📍 " + post["Location"] + ", " + post["Country"] + "<br/>"
	out = out + "🎨 " + post["Opportunity Discipline"] + "<br/>"
	out = out + "📅 " + post["Application Deadline"] + " deadline" + "<br/>"
	feeInfo = ""
	if post["Application Fee"] == " ":
		feeInfo = "unknown fee"
	else:
		feeInfo = post["Application Fee"] + " fee"
	out = out + "💰 " + feeInfo + "<br/>"
	out = out + "➡ " + "<a href=\""+post["Website"]+"\">"+"Apply"+"</a>" + "</p>"
	out = out  +"<p><strong>" + "===== DESCRIPTION ======" + "</strong></p>"
	out = out + "<p>" + post["Description"] + "</p>"
	out = out  +"<p><strong>" + "===== INSTRUCTIONS =====" + "</strong></p>"
	out = out + "<p>" + post["Application Instructions"] + "</p>"

	return out


# Save a list of items to an rss xml feed file
def saveFeed(listings, title, path):

	url = githubRepoURL + title + ".xml"

	# Create a feed generator
	fg = FeedGenerator()

	# Create the feed's title
	fg.id(url)
	fg.title(title)
	fg.author({'name':'Ben Snell'})
	fg.description("Art Show Open Call Opportunities")
	fg.link( href=url, rel='alternate' )
	fg.language('en')
	time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') + "-05:00"
	fg.pubDate(time)
	fg.updated(time)

	for item in listings:

		e = fg.add_entry()
		
		e.id( item["ID"] )
		e.title( item["Title"] )
		# for key, value in item.items():
			# print(key, value);
		# print(item["url"])
		# if "url" in item:
		e.link( href=item["url"] )

		text = getHtmlFormattedListing(item)
		e.content( type="html", content=text )

		# This doesn't seem to work:
		# e.pubDate( datetime2RSSString(clDate(apt[2])) )
		# e.updated( datetime2RSSString(clDate(apt[2])) )

	fg.atom_str(pretty=True)
	fg.atom_file(path)


def process():

	# Get listings
	listings = getAllListings(listingsURL, 10)
	if (listings == None): return

	# Get recent post ID's
	listingTypes = ["Call for Entry/Open Call"]
	recentIDs = parseListings(listings, listingTypes)

	# Get the new post IDs
	newIDs = getNewListings(recentIDs)

	# Get the attributes for each id (create a dict for each)
	objects = getAllListingsAttributes(newIDs)

	# Save all of these objects to the database
	saveToDB(db, objects)

	# Get all items observed within the last includeSec
	lastItems = getLastItems(db, includeSec)

	# Save these items to an xml rss file
	saveTitle = "open-calls"
	savePath = getWorkingDir() + "/feeds/" + saveTitle + ".xml";
	saveFeed(lastItems, saveTitle, savePath)

	# Upload items to github
	uploads = []
	uploads.append(getWorkingDir() + "/feeds/" + saveTitle + ".xml")
	uploads.append(getWorkingDir() + "/" + "db.json")
	repo = Repo("../" + repoName)
	repo.index.add(uploads)
	repo.index.commit("Updated feeds")
	origin = repo.remote('origin')
	origin.push()


def main():

	print("Starting Process ------------------------")

	# Run code
	start = time.time()
	process()
	stop = time.time()

	print("Ending Process ------------------------Waiting...")

	# Get duration in seconds
	duration = stop - start

	# Wait for no more than 15 minutes
	time.sleep(max(refreshSec - duration, 0))

	print("... Done waiting")


if __name__ == "__main__":
	main()
