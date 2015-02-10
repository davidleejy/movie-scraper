from bs4 import BeautifulSoup
#from urllib2 import urlopen
import urllib2
import re,sys

# IMDB
BASE_URL = "http://www.imdb.com"
movie_rating = 0
movie_description = ""

# Rotten Tomatoes
rottenBaseURL = "http://www.rottentomatoes.com"
rottenMoviePagePath = rottenBaseURL + "/m/"
rottenSearchPath = rottenBaseURL + "/search/?search="
movieDesc = ""


# ---------------------
# Rotten Tomatoes


# Returns the html content of a movie's Rotten Tomato page.
# REQUIRES: Movie title. Leave the spaces in the movie's title
#           as spaces.  E.g. "Walter Mitty", "Anna and the king of Siam"
# EXCEPTIONS: e.g 404 page not found.
# RETURNS: A urllib2 "file-like object". Words in apostrophes are
#           quoted from urllib2's documentation.
def getRottenMoviePage(movie):
    movieAsURL = movie.lower().replace(" " , "_")
    movieAsURL = re.sub("[\W]+", "", movieAsURL)
    try:
        page = urllib2.urlopen(rottenMoviePagePath + movieAsURL)
    except urllib2.HTTPError, e:
        print "Error: " + str(e.code)
        return None
    except urllib2.URLError, e:
        print "Error: " + str(e.args)
        return None
    else:
        #print "succ"
        return page
    return

# Returns the Rotten Tomatoes search page for a given movie
# name.
# REQUIRES: Movie title.
# EXCEPTIONS: HTTPError and URLError
# RETURNS: A urllib2 "file-like object". Words in apostrophes are
#           quoted from urllib2's documentation.
def rottenSearch(movie):
    try:
        movieURLEnc = urllib2.quote(movie)
        page = urllib2.urlopen(rottenSearchPath + movieURLEnc)
    except urllib2.HTTPError, e:
        print "Error: " + str(e.code)
        return None
    except urllib2.URLError, e:
        print "Error: " + str(e.args)
        return None
    else:
        return page
    return

# Identify what searching for a movie led to.
# REQUIRES: page obtained after searching (after calling
#           rottenSearch(.) .
# RETURNS: 1 search redirected to movie page.
#          2 search results > 0.
#          3 search results == 0.
#          4 unknown.
#          None searchPage is None.
def identifySearchResults(searchPage):
    if searchPage is None:
        return None
    url = searchPage.geturl()
    k = rottenMoviePagePath.find("http://www.")+len("http://")
    moviePageSignature = rottenMoviePagePath[k:]
    match = re.search(moviePageSignature, url)
    if not match is None:
        return 1
    else:
        soup = BeautifulSoup(searchPage)
        divResults = soup.find("a", id="movies_tab", href="#results_movies_tab")
        if not divResults is None:
            print divResults.contents[0]
            return 2
        divSorry = soup.find("h1", class_="center noresults")
        if not divSorry is None:
            return 3
    return 4



# Returns the movie description of a Rotten Tomato page.
# REQUIRES: A Rotten Tomato movie page as a urllib2 
#           "file-like object".
# RETURNS: Movie description as string.
def getRottenMovieDescription(page):
    if page is None:
        return None
    soup = BeautifulSoup(page)

    # Long Movie descriptions are truncated.

    div = soup.find("p", id="movieSynopsis", class_="movie_synopsis")
    desc = div.contents[0]
    desc = desc.strip()
    div2 = div.find("span", id="movieSynopsisRemaining", style="display: none;")
    if div2 != None:
        desc += div2.contents[0]

    return desc




#--------------
#IMDb

#TODO: GLOBAL VARIABLES WTH!!!

#
#   Print the details of the found movie
#

def print_details(movie_description,movie_rating):
    print "Movie Name : " + movie
    print "Movie Rating : " + movie_rating
    print "Movie Description : " + movie_description
    return

#
#   Get the details of the found movie. Scrape throu' for director and rating.
#   More details to be added.
#

def get_details(link):
    page = urllib2.urlopen(link)
    soup = BeautifulSoup(page)
    div = soup.find('div', class_="titlePageSprite")
    movie_rating = div.contents[0]
    div = soup.find('p', itemprop="description")
    movie_description = div.contents[0] 
    DivDirector = soup.find('div', itemprop="director")
    director = DivDirector.find('span', itemprop="name")
    movie_director = director.contents[0]
    print_details(movie_description,movie_rating)
    return

#
#   Find the movie, using imdb/find? tag. Get the first matched movie.
#

def get_category_links(movie):
    page = urllib2.urlopen(BASE_URL +"/find?" + movie)
    soup = BeautifulSoup(page)
    div = soup.find('table', class_="findList")
    links = div.find('a', href=True)

    complete_link = BASE_URL + links['href']
    #print "complete link:" + complete_link
    get_details(complete_link)
    return
def format_movie():
    movie.replace(" ","-")
    return









args = " ".join(sys.argv[1:]) 
argList = args.split(",,,")
movie = argList[0]
#print(movie)
IMDbURL = None
if len(argList) == 2:
    IMDbURL = argList[1]


print("Title: " + movie)
print("IMDbURL: " + str(IMDbURL))


print "-----------------"
print "Rotten Tomatoes"
print "-----------------"

rottenDesc = None

moviePage = getRottenMoviePage(movie)

if moviePage is None:
    print "Searching with movie title instead " + \
            "of directly getting the movie's page. " + \
            "Please wait."
    sPage = rottenSearch(movie)
    #print(len(sPage.read()))  #TODO
    searchPageIdentity = identifySearchResults(sPage)
    print "Search page identity: " + str(searchPageIdentity)

    if searchPageIdentity == 1:
        # Searching redirected us to the actual movie page.
        rottenDesc = getRottenMovieDescription(sPage)
    elif searchPageIdentity == 2:
        # Click on first link to go to movie page.
        sPage2 = rottenSearch(movie)
        sPageSoup2 = BeautifulSoup(sPage2.read())
        #print(len(sPage.read()))
        #print(type(sPageSoup))
        link = sPageSoup2.find("div", id="tabs", class_="ui-tabs").find("ul", id="movie_results_ul").find('a', href=True)['href']
        complete_link = rottenBaseURL + link
        moviePage = urllib2.urlopen(complete_link)
        rottenDesc = getRottenMovieDescription(moviePage)
    else:
        # Case of 0 search results OR unknown.
        rottenDesc = None
else:
    # Able to find the movie page directly.
    rottenDesc = getRottenMovieDescription(moviePage)

if rottenDesc is None:
    rottenDesc = "None found."
print "Description: " + rottenDesc



print "-----"
print "IMDB"
print "-----"

if IMDbURL is None:
    movie = movie.replace(" ","-")
    get_category_links(movie)
else:
    get_details(IMDbURL)



