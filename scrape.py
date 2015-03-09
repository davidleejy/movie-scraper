from bs4 import BeautifulSoup
#from urllib2 import urlopen
import urllib2
import re,sys
import string
import traceback
from collections import namedtuple

# IMDB
BASE_URL = "http://www.imdb.com"
IMDb_Details = namedtuple("IMDb_Details", "rating director description")

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

# Prints a IMDb_Details namedtupl object.
def print_details(details):
  try:
    print "Director: " + details.director
    print "Rating: " + details.rating
    print "Description: " + details.description
    return
  except:
    print "Unrecognizable details provided."
    print traceback.format_exc()


# Get a movie's details given an IMDb URL.
# EXCEPTIONS: raise.
def get_imdb_details(url):
  try:
    page = urllib2.urlopen(url)
    soup = BeautifulSoup(page)
    div = soup.find('div', class_="titlePageSprite")
    movie_rating = div.contents[0]
    div = soup.find('p', itemprop="description")
    movie_description = div.contents[0] 
    DivDirector = soup.find('div', itemprop="director")
    director = DivDirector.find('span', itemprop="name")
    movie_director = director.contents[0]
    return IMDb_Details(rating=movie_rating,director=movie_director,description=movie_description)
  except:
    raise

# Get a movie's IMDb page URL.
# EXCEPTIONS: raised.
def get_imdb_page_url(movie):
    try:
      page = urllib2.urlopen(BASE_URL +"/find?" + movie.replace(" ", "-"))

      soup = BeautifulSoup(page)
      div = soup.find('table', class_="findList")

      links = div.find_all("td", class_="result_text")
      
      # Try exact matching
      idx=exact_match_imdb_search_results(links,movie)
      if idx != -1: # Try approximate matching
        print "Exact match found in search results. Picked entry " + str(idx)
      else:
        idx=approx_match_imdb_search_results(links,movie)
        if idx != -1:
          print "Approximate match found in search results. Picked entry " + str(idx)
        else:
          title_without_punctuation=movie.translate(string.maketrans("",""), string.punctuation)
          idx=approx_match_imdb_search_results(links,title_without_punctuation)
          if idx != -1:
            print "Approximate match found (after stripping title of punctuation) in search results. Picked entry " + str(idx)
          else:
            idx=0 
            print "No exact or approximate matches in search results. Picked first search result entry. (index 0)."

      link = links[idx].find('a', href=True)
      return  BASE_URL + link['href']
    except:
      raise


# Finds a result entry that matches exactly the movie title.
def exact_match_imdb_search_results(results,movie):
  idx=0
  for entry in results:
    text=entry.text
    if string.find(text.lower(),movie.lower()) != -1:
        return idx
    idx+=1
  return -1 # Failed


# Finds a result entry that best matches the movie title.
def approx_match_imdb_search_results(results,movie):
  best_index=-1
  best_similarity=0.0
  movie_words=movie.lower().split(" ")
  cur_index=0
  for entry in results:
    text=entry.text.lower()
    #print("ap   " + text)
    matchCount=0
    for w in movie_words:
      if string.find(text, w) != -1:
        matchCount+=1
        #print(w + " matches!")
    similarity=matchCount/len(movie_words)
    #print("similarity=" + str(similarity))
    if similarity > best_similarity:
      best_similarity=similarity
      best_index=cur_index
    cur_index+=1
  return best_index








args = " ".join(sys.argv[1:]) 
argList = args.split(",,,")
movie = argList[0]
#print(movie)
IMDbURL = None
if len(argList) == 2:
    IMDbURL = argList[1]


print("Title: " + movie)
print("IMDbURL: " + str(IMDbURL))




print "-----"
print "IMDB"
print "-----"
imdb_details=None
if IMDbURL is None:
  try:
    page_url=get_imdb_page_url(movie)
    imdb_details=get_imdb_details(page_url)
  except:
    print("Extraction failed.")
    print traceback.format_exc()
else:
  try:
    imdb_details=get_imdb_details(IMDbURL)
  except:
    print("Extraction failed.")
    print traceback.format_exc()
if not imdb_details is None:
  print_details(imdb_details)





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

