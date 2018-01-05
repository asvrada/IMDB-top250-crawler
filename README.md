# IMDB Top 250 Crawler

This crawler crawls all the movies from [this page](http://www.imdb.com/chart/top), including each movie's title, director(s), year of release and more

### Dependency:
* Scrapy 1.5+
* BeautifulSoup 4+

### To Run:
`cd scrapy_version/IMDBTop && scrapy crawl top_movies`   
Or better to save the result to a json file:  
`cd scrapy_version/IMDBTop && scrapy crawl top_movies -o data.json`  

> `/sort_data.py` simply sort the result by IMDB rank in ascending order in place

### Result
You can check the output of this crawler here  
[data.json](scrapy_version/IMDBTop/data.json)