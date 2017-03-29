import urllib.request
from urllib.parse import urljoin
import re
from bs4 import BeautifulSoup
from collections import deque
import string

def crawl(seedUrlList, relatedTermList, destinationFolderPath):
    queue = deque()
    visitedUrlList = []
    crawledPages = 0
    titles = []

    for seedUrl in seedUrlList:
        queue.append(seedUrl)

    while len(queue) > 0 and crawledPages < 600:
        currentUrl = queue.popleft()
        
        if currentUrl not in visitedUrlList:
            try:
                print("trying " + currentUrl)
                visitedUrlList.append(currentUrl)
                html = urllib.request.urlopen(currentUrl).read().decode('utf-8')            
            except:
                continue

            soup = BeautifulSoup(html, 'html.parser')

            #get title from page
            if soup.title is None:
                continue
            title = soup.title.string
            title = clean_title(title)

            #check page title
            if title in titles or "Pages that link to" in title or "Changes related to" in title:
                continue
            titles.append(title)

            relatedTerms = 0
            text = soup.get_text()
            
            for relatedTerm in relatedTermList:
                if re.search("[^A-Z0-9-]" + relatedTerm + "[^A-Z0-9-]", text, re.IGNORECASE):
                    relatedTerms += 1

                    if relatedTerms >= 2:
                        break

            if relatedTerms >= 2:
                #save page - using title as filename            
                file = open(destinationFolderPath + title + ".html", "wb")
                file.write(soup.prettify('utf-8'))
                file.close()

                print("page is relevant!")

                crawledPages += 1

                #add page's links to queue - if they are valid
                for link in soup.find_all('a'):
                    url = link.get('href')
                    joinedUrl = urljoin(currentUrl, url)
                    
                    if is_valid_url(joinedUrl):
                        joinedUrl = url_shorten(joinedUrl)   
                        queue.append(joinedUrl)

    
    #save urls to file
    file = open(destinationFolderPath + "urls.txt", "w")
    for url in visitedUrlList:
        file.write(url + "\n")
    file.close()

def clean_title(title):
    for c in title:
        if c not in " -" and c not in string.ascii_letters and c not in string.digits:
            title = title.replace(c, '')

    return title

def url_shorten(url):
    if url.find('#') != -1:
        url = url[:url.find('#')]
    return url

def is_valid_url(url):
    return url is not None and "en.wikipedia.org" in url and "index.php?" not in url

seedUrlList = ["https://en.wikipedia.org/wiki/Video_game",
               "https://en.wikipedia.org/wiki/List_of_video_games_considered_the_best"]

relatedTermList = ["Video Game", "Console", "Nintendo",
                   "Microsoft", "Xbox", "Playstation", "Sony",
                   "Sega", "Game Design", "Steam",
                   "Indie", "Downloadable Content",
                   "Emulator", "gamer", "multiplayer"]

destinationFolderPath = "E:\\Users\\Kevyn\\Desktop\\crawled\\"

crawl(seedUrlList, relatedTermList, destinationFolderPath)
