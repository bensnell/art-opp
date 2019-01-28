import os
import sys
import requests

# ========== PARAMS ============

# Url to get the listings
postUrl = "https://www.nyfa.org/Opportunities/Search"

# =========== CODE =============

# Try to get the url
resp = None
try:
	resp = requests.post(postUrl)
except:
	print("Could not retrieve the url " + postUrl)

# Parse the information
newOC = []
if resp != None:
	data = resp.json()["Regular_Listings"]
	# Find all open calls
	for opp in data:
		if opp["OppType"] == "Call for Entry/Open Call":
			newOC.append(opp)

# Add all new open calls to an RSS feed



# Save the new open calls to a database



