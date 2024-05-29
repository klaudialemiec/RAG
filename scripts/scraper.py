import re

import requests
from bs4 import BeautifulSoup


class BasicScrapper:
    """
    A class that performs basic web scraping operations.

    Attributes:
        None

    Methods:
        crawl(url: str) -> dict:
            Crawls the given URL and returns a dictionary containing the scraped content, title, and URL.

        clean_soup(html_soup: str) -> str:
            Removes navigation bars, banners, footers, feedbacks, logos, and authors tags from the HTML.

        clean_html_text(text: str) -> str:
            Cleans the HTML text by removing excessive newlines.

    """

    def crawl(self, url: str) -> dict:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")
        title = soup.title.get_text()
        clean_soup = self.clean_soup(soup)
        content = self.clean_html_text(clean_soup.get_text())

        return {"content": content, "title": title, "url": url}

    def clean_soup(self, html_soup: str) -> str:
        """Remove navigation bars, banners, footers, feedbacks, logos and authors tags from html"""
        nav_bars = html_soup.find_all("div", {"role": "navigation"})
        nav_bars2 = html_soup.find_all("div", {"class": re.compile(".*nav.*__.*")})
        nav_bars3 = html_soup.find_all("a", {"class": re.compile(".*nav.*__.*")})
        nav_bars4 = html_soup.find_all("nav")
        links = html_soup.find_all("a", {"class": re.compile(".*jump-link")})
        banners = html_soup.find_all("div", {"class": "show-banner"})
        footers = html_soup.find_all("footer")
        feedbacks = html_soup.find_all("div", {"class": re.compile("feedback")})
        logos = html_soup.find_all("div", {"class": re.compile("logo")})
        authors = html_soup.find_all("div", {"class": re.compile("author")})
        dropdown = html_soup.find_all("div", {"class": re.compile("dropdown")})
        search1 = html_soup.find_all("span", {"role": "search"})
        search2 = html_soup.find_all("div", {"class": re.compile("search")})
        vector_menu = html_soup.find_all("div", {"class": re.compile("vector-menu")})
        buttons = html_soup.find_all("button")

        to_remove = (
            nav_bars
            + nav_bars2
            + nav_bars3
            + nav_bars4
            + footers
            + banners
            + feedbacks
            + logos
            + authors
            + links
            + dropdown
            + search1
            + search2
            + vector_menu
            + buttons
        )

        for fragment in to_remove:
            fragment.extract()

        return html_soup

    def clean_html_text(self, text: str) -> str:
        text = text.strip("\n")
        return re.sub("(\\n[\s]*){3,}", "\n\n", text)
