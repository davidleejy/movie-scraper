# Movie Scraper

## Description
A web scraper that scrapes movie-related websites like Rotten Tomatoes and IMDb.



## Basic Requirements
python 2.7.x

Python libraries used in code (e.g. Beautiful Soup 4).



## Usage
python scrape.py *movie title*

or

python scrape.py *movie title*,,,*IMDb URL of movie*

The 3 commas act as a delimiter, separating the arguments - title and IMDb URL.



**Examples:**

```
$ python scrape.py guardians of the galaxy,,,http://www.imdb.com/title/tt2015381
```
![Guardians Example]
(http://i.imgur.com/rIgkaJh.png)
________

```
$ python scrape.py black swan
```
![Black Swan Example]
(http://i.imgur.com/Htj7lWq.png)
________

```
$ python scrape.py walter mitty,,,http://www.imdb.com/title/tt0359950/
```
![Walter Mitty Example]
(http://i.imgur.com/5NhdMVZ.png)




