from habanero import Crossref
import requests
import logging
import sys
import time
import re

cr = Crossref()

# useage ~python wiley_doi_retrieval.py "myContactFile.txt" "DOIfile.txt"

# myContactFile.txt should have format:
# your_url
# your_email
# your_wiley_api_token

if __name__ == '__main__':
    contactFile = sys.argv[1]
    # store your contact info to be on the polite list (crossref) as well as your Wiley API token
    # alternatively edit this section to just load your API token
    with open(contactFile, "r") as fp:
        base_url = fp.readline().rstrip('\n')
        mailto = fp.readline().rstrip('\n')
        clickThroughKey = fp.readline().rstrip('\n')

    # setup Crossref
    cr = Crossref()
    Crossref(base_url=base_url)
    Crossref(mailto=mailto)

    # load DOIs
    #The DOI file should look like a text file with line after line of DOIs:
    #10.234234/235235
    #122.4334234/15151253
    #etc.....

    doiFile = sys.argv[2]
    doiList = []
    with open(doiFile, 'r') as fp:
        for line in fp:
            doiList.append(line.rstrip('\n'))

    # setup logging environment
    logging.getLogger().setLevel(logging.DEBUG)
    requests_log = logging.getLogger("requests.packages.urllib3")
    requests_log.setLevel(logging.DEBUG)
    requests_log.propagate = True

    # retrieve links to DOIs through crossref:
    articleList = []
    for item in doiList:
        print("searching for DOI:" + item )
        # filter={'has_full_text': True, 'type':'journal-article', 'full-text.application': 'text-mining'})
        res = cr.works(ids=item)
        print("found"+ res['message']['title'][0])
        article = res['message']
        print("getting link to: " +article['title'][0])
        if article['link'][0]['intended-application'] == 'text-mining':  #double check you get the right url
            #store as a tuple with (URL,title)
            print("success")
            articleList.append((article['link'][0]['URL'], re.sub(r'\W+','',article['title'][0])))
        else:
            print("url error")
            break
    # retrieve PDFs through Wiley API (Can fork this and change this to other API's e.g. elsevier if needed)
    header = {'CR-Clickthrough-Client-Token': clickThroughKey}
    for article in articleList:
        r = requests.get(article[0], allow_redirects=True, headers=header)
        #you might also consider prefixing all the pdfs with something to make them easier to find.
        with open(article[1].replace(" ","")[:15]+ ".pdf", 'wb') as fp:
            fp.write(r.content)
        time.sleep(10) #this time should be generous enough to avoid rate limits.

