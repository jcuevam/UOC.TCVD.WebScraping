import requests
from bs4 import BeautifulSoup


class Scraper:

    const_comics_category = "/comics/"

    def __init__(self):
        print("Scraper inicialitzat")

    def request_html(self, url):
        return requests.get(url)

    def save_html(self, html, file_name):
        with open(f"data/{file_name}", 'wb') as f:
            f.write(html)

    def open_html(self, file_name):
        with open(f"data/{file_name}", 'rb') as f:
            return f.read()

    def get_content_links(self, html):
        soup = BeautifulSoup(html, 'html.parser')

        catalog = soup.select("ul li")
        categories = [category.text.strip() for category in catalog]

        a_tags = [category.select_one('a') for category in catalog]
        comics_links = [a_tag['href'] for a_tag in a_tags if a_tag is not None and self.const_comics_category in a_tag['href']]

        comics_links_names = self.get_content_links_names(comics_links)

        requests = [self.request_html(link) for link in comics_links]
        for request, name in zip(requests, comics_links_names):
            self.save_html(request.content, name)

        return comics_links_names

    def get_content_links_names(self, links):
        return [link.split(self.const_comics_category)[1] for link in links]


    def scrape(self):
        """
        Funció main de la nostra classe Scraper.
        :param config: JSON amb els paràmetres de configuració.
        :return:
        """

        # Accedim a la url i guardem el contingut en local per no haver de tornar a accedir

        url = 'https://www.ecccomics.com/'
        # r = self.request_html(url)

        # self.save_html(r.content, 'data/ecccomics')
        html = self.open_html('ecccomics')

        # BeautifulSoup

        comics_links = self.get_content_links(html)


