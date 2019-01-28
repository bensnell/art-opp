import os
import sys
import requests
from tinydb import TinyDB, Query

# Get the current location of this script


# ========== PARAMS ============

# Url to get the listings
postUrl = "https://www.nyfa.org/Opportunities/Search"

# Create a database if one doesn't exist
db = TinyDB("db.json")

# =========== CODE =============

# Try to get the url
resp = None
try:
	resp = requests.post(postUrl)
except:
	print("Could not retrieve the url " + postUrl)

# Parse the information for opportunities
recentOpp = []
if resp != None:

	try:
		data = resp.json()["Regular_Listings"]
		# Find all open calls
		for opp in data:
			if opp["OppType"] == "Call for Entry/Open Call":
				recentOpp.append(opp)
	except:
		print("Something went wrong!")

# Find all of the new oppportunities
newOpp = []
for opp in recentOpp:
	if 




# Add all new open calls to an RSS feed



# Save the new open calls to a database




def main():

	while (True):





if __name__ == "__main__":
	main()

