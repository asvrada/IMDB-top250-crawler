# Packages in repo
import requests
import re
import json
from bs4 import BeautifulSoup

# Local Package
from Helper import Helper

# Package for debugging
from Data import PrefetchedData


# Constants
# URL_IMDB_MAIN = r"http://www.imdb.com/chart/top"
URL_IMDB_MAIN = r"http://www.imdb.com/chart/top?sort=ir,desc&mode=simple"
URL_IMDB_MOVIE_PREFIX = r"http://www.imdb.com/title/"


class BasePage:
    def __init__(self, url):
        self.url_page = url
        download_page = requests.get(self.url_page).text
        self.bsoup = BeautifulSoup(download_page, "html.parser")


class IMDBMainPage(BasePage):
    def __init__(self, url):
        super().__init__(url)
        self.data_movies = []

    @staticmethod
    def regex_get_movie_id(full_url):
        """
        Layout for full_url
        /title/tt0111161/?pf_rd_m=A2FGELUUNOQJNL&pf_rd_p=3376940102&pf_rd_r=0EGKAP8Z7MG82QADVKMV&pf_rd_s=center-1&pf_rd_t=15506&pf_rd_i=top&ref_=chttp_tt_1
        :param full_url: the url to be parsered
        :return: movie_id
        """
        re_pattern = re.compile(r"/title/([^/]*)/")
        matchs = re.match(re_pattern, full_url)
        return matchs.group(1)

    @staticmethod
    def get_movie_id_from_html(movie_block):
        """
        Get the id of the movie

        :param movie_block: HTML tr element
        :type movie_block bs4.element.Tag
        :return: string movie id
        """
        title_column = movie_block.find("td", class_="titleColumn")
        full_url = title_column.find("a")["href"]

        # Example: tt0111161
        movie_id = IMDBMainPage.regex_get_movie_id(full_url)

        return movie_id

    @staticmethod
    def analyze_given_url(full_url):
        return MoviePage(full_url)

    def analyze(self, start=None, end=None):
        def process_each_movie(movie):
            movie_id = self.get_movie_id_from_html(movie)
            movie = self.analyze_given_url(movie_id)
            return movie.data_movie

        # Get all 250 cells in the table
        list_movies = self.bsoup.find_all("tbody", class_="lister-list")[0].find_all("tr")

        self.data_movies = [process_each_movie(movie) for movie in list_movies[start: end]]

        return self


class MoviePage(BasePage):
    def __init__(self, url):
        super().__init__(URL_IMDB_MOVIE_PREFIX + url)
        self.data_movie = {
            "id": url,
            "title": None,
            "poster_url": None,
            "year": None,
            "directors": None,
            "genres": None,
            "length": None,
            "imdb_rating": None,
            "imdb_rank": None,
            "metascore": None
        }
        self.analyze()

    def get_title(self):
        # div .title_wrapper
        # Return Tag
        tag_title = self.bsoup.find("div", class_="title_wrapper").h1

        # Sample Content:
        # "One Flew Over the Cuckoo's Nest\xa0(1975)"
        title = tag_title.text.strip()
        title = title.replace(u'\xa0', '')
        title = re.sub(r"\(\d*\)", "", title)

        return title

    def get_poster_url(self):
        # div .slate_wrapper
        # div .minPosterWithPlotSummaryHeight > img
        try:
            tag_poster = self.bsoup.find("div", class_="slate_wrapper") \
                         or self.bsoup.find("div", class_="minPosterWithPlotSummaryHeight")

        except Exception:
            print("Failed to fetch poster url: " + self.url_page)
            return None

        return tag_poster.img["src"]

    def get_year(self):
        # div .title_wrapper
        # Return Tag
        tag_title = self.bsoup.find("div", class_="title_wrapper").h1

        # Sample Content:
        # "One Flew Over the Cuckoo's Nest\xa0(1975)"
        title = tag_title.text
        year = re.findall(r"\((\d*)\)", title)[0]

        return int(year)

    def get_directors(self):
        def get_id_name_of_director_from_html(tag):
            url = tag["href"][6:15]
            name = tag.text

            return url, name

        # div .plot_summary_wrapper
        tag = self.bsoup.find("div", class_="plot_summary_wrapper").find("div", class_="plot_summary").find_all("div")[
            1]

        '''
        Sample Layout
        <div class="credit_summary_item">
            <h4 class="inline">Director:</h4>
            <span itemprop="director" itemscope="" itemtype="http://schema.org/Person">
                <a href="/name/nm0001232?ref_=tt_ov_dr" itemprop="url"><span class="itemprop" itemprop="name">Milos Forman</span></a>
            </span>
            <span itemprop="director" itemscope="" itemtype="http://schema.org/Person">
                <a href="/name/nm0001232?ref_=tt_ov_dr" itemprop="url"><span class="itemprop" itemprop="name">Milos Forman</span></a>
            </span>
        </div>
        '''
        elements = tag.find_all("a")

        ret = []
        # Get Director ID
        # Get Director Name
        for each in elements:
            director_id, director_name = get_id_name_of_director_from_html(each)
            ret.append({
                "id": director_id,
                "name": director_name
            })

        return ret

    def get_genre(self):
        title_wrapper = self.bsoup.find("div", class_="title_wrapper")
        elements_a = title_wrapper.find_all("a")
        return [each.text for each in elements_a[1:-1]]

    def get_length(self):
        title_wrapper = self.bsoup.find("div", class_="title_wrapper")
        time = title_wrapper.find("time")
        return Helper.get_duration_from_time_string(time.text.strip())

    def get_imdb_rating(self):
        rating = self.bsoup.find("div", class_="ratingValue")

        return float(rating.span.text.strip())

    def get_imdb_rank(self):
        rank = self.bsoup.find("div", id="titleAwardsRanks")
        return int(rank.a.text[19:])

    def get_metascore(self):
        # div .metacriticScore
        try:
            meta_score = self.bsoup.find("div", class_="metacriticScore")

            if not meta_score:
                return None

            meta_score = int(meta_score.span.text)
        except Exception:
            print("Failed to get meta score: " + self.url_page)
            return None

        return meta_score

    def get(self, column):
        options = {
            "title": self.get_title,
            "poster_url": self.get_poster_url,
            "year": self.get_year,
            "directors": self.get_directors,
            "genres": self.get_genre,
            "length": self.get_length,
            "imdb_rating": self.get_imdb_rating,
            "imdb_rank": self.get_imdb_rank,
            "metascore": self.get_metascore
        }
        return options[column]()

    def analyze(self):
        """
        Goal: Get the following information from movie
        1. title
        2. URL to poster
        3. Year of release (USA)
        4. Director
        5. genre
        6. Length
        7. IMDB Rating
        8. IMDB Rank
        9. Metascore
        :return:
        """
        for k in self.data_movie:
            # We already got ID when __init__
            if k == "id":
                continue
            self.data_movie[k] = self.get(k)


main_page = IMDBMainPage(URL_IMDB_MAIN)
main_page.analyze()

print(json.dumps(main_page.data_movies))
