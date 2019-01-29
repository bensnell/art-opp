import os
import sys
import requests
from tinydb import TinyDB, Query
import re
import time

# Get the current working directory
def getWorkingDir():
	return os.path.dirname(os.path.abspath(__file__))

# ========== USERPARAMS ============

# Url to get the listings
listingsURL = "https://www.nyfa.org/Opportunities/Search"

# Create a database if one doesn't exist
db = TinyDB(getWorkingDir() + "/" + "db.json")

# Number of seconds to refresh
refreshSec = 60*60 # every hr

# =========== CODE =============

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
	return response

def getAllListings(URL, maxPages):

	out = []
	for i in range(1, maxPages+1):
		pagelistings = getListings(URL, i)
		if pagelistings == None:
			break
		out = out + pagelistings
	return list(set(out))

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

def getOrganization(opp, text):
	try:
		obj = re.search( r'Organization</div><div class=\"info-right-column mobile-width-100-center\">\s*(.*?)\s*</div>', x.text, re.M|re.I|re.S)
		opp["Organization"] = obj.group(1).strip()
	except:
		print("Could not retrieve organization information for "+opp["ID"])
		opp["Organization"] = ""
		return False
	return True

def getWebsite(opp, text):
	try:
		obj = re.search( r'Website</div><div class=\"info-right-column mobile-width-100-center\">\s*<a href=\"\s*(.*?)\s*\" target=\"_blank\"', x.text, re.M|re.I|re.S)
		opp["Website"] = obj.group(1).strip()
	except:
		print("Could not retrieve website information for "+opp["ID"])
		opp["Website"] = ""
		return False
	return True

def getCountry(opp, text):
	try:
		obj = re.search( r'Country</div><div class=\"info-right-column mobile-width-100-center\">\s*(.*?)\s*</div>', x.text, re.M|re.I|re.S)
		opp["Country"] = obj.group(1).strip()
	except:
		print("Could not retrieve country information for "+opp["ID"])
		opp["Country"] = ""
		return False
	return True

def getLocation(opp, text):
	try:
		obj = re.search( r'Location</div><div class=\"info-right-column mobile-width-100-center\">\s*(.*?)\s*</div>', x.text, re.M|re.I|re.S)
		opp["Location"] = obj.group(1).strip()
	except:
		print("Could not retrieve location information for "+opp["ID"])
		opp["Location"] = ""
		return False
	return True

def getOpportunityType(opp, text):
	try:
		obj = re.search( r'Opportunity Type</div><div class=\"info-right-column mobile-width-100-center\">\s*(.*?)\s*</div>', x.text, re.M|re.I|re.S)
		opp["Opportunity Type"] = obj.group(1).strip()
	except:
		print("Could not retrieve opportunity type information for "+opp["ID"])
		opp["Opportunity Type"] = ""
		return False
	return True

def getOpportunityDiscipline(opp, text):
	try:
		obj = re.search( r'Opportunity Discipline</div><div class=\"info-right-column mobile-width-100-center\">\s*(.*?)\s*</div>', x.text, re.M|re.I|re.S)
		opp["Opportunity Discipline"] = obj.group(1).strip()
	except:
		print("Could not retrieve opportunity discipline information for "+opp["ID"])
		opp["Opportunity Discipline"] = ""
		return False
	return True

def getApplicationFee(opp, text):
	try:
		obj = re.search( r'Application Fee</div><div class=\"info-right-column mobile-width-100-center\">\s*(.*?)\s*</div>', x.text, re.M|re.I|re.S)
		opp["Application Fee"] = obj.group(1).strip()
	except:
		print("Could not retrieve application fee information for "+opp["ID"])
		opp["Application Fee"] = ""
		return False
	return True

def getApplicationDeadline(opp, text):
	try:
		obj = re.search( r'Application Deadline</div><div class=\"info-right-column mobile-width-100-center\">\s*(.*?)\s*</div>', x.text, re.M|re.I|re.S)
		opp["Application Deadline"] = obj.group(1).strip()
	except:
		print("Could not retrieve application deadline information for "+opp["ID"])
		opp["Application Deadline"] = ""
		return False
	return True

# Issue: https://stackoverflow.com/questions/20056306/match-linebreaks-n-or-r-n
def getDescription(opp, text):
	try:
		obj = re.search( r'Description</h2>\s*<div class=\"projectDetailsDiv text-justify text-pre-wrap\">\s*(.*?)\s*</div>', x.text, re.M|re.I|re.S)
		opp["Application Deadline"] = obj.group(1).strip()
	except:
		print("Could not retrieve application deadline information for "+opp["ID"])
		opp["Application Deadline"] = ""
		return False
	return True

def getApplicationInstructions(opp, text):
	try:
		obj = re.search( r'Application Instructions / Public Contact Information</h2>\s*<div class=\"projectDetailsDiv text-justify text-pre-wrap\">\s*(.*?)\s*</div>', x.text, re.M|re.I|re.S)
		opp["Application Instructions"] = obj.group(1).strip()
	except:
		print("Could not retrieve application instructions information for "+opp["ID"])
		opp["Application Instructions"] = ""
		return False
	return True



# Get the attributes of each opportunity
fullOpp = []
for opp in newOpp:



	thisUrl = "https://www.nyfa.org/Opportunities/Show/"+opp["ID"]

	text
	try:
		# Get the page
		text = getListingHTMLText(thisUrl)
		if text == None: break

		# A new container for "get" data
		thisOpp = {}

		# Get all matches  and populate the new dictionary
		getOrganization(thisOpp, text)
		getWebsite(thisOpp, text)
		getCountry(thisOpp, text)
		getLocation(thisOpp, text)




			



# Add all of the new opportunities to the RSS feed




# Add all new open calls to an RSS feed



# Save the new open calls to a database


def process():

	# Get listings
	listings = getAllListings(listingsURL, 10)
	if (listings == None): return

	# Get recent post ID's
	listingTypes = ["Call for Entry/Open Call"]
	recentIDs = parseListings(listings, listingTypes)

	# Get the new post IDs
	newIDs = getNewListings(recentIDs)









	# TODO: Embed links




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
