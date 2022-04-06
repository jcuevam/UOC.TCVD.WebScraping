import requests
from bs4 import BeautifulSoup


class Scraper:

    def __init__(self):
        print("Scraper inicialitzat")

    def save_html(self, html, path):
        with open(path, 'wb') as f:
            f.write(html)

    def open_html(self, path):
        with open(path, 'rb') as f:
            return f.read()


    def scrape(self):
        """
        Funció main de la nostra classe Scraper.
        :param config: JSON amb els paràmetres de configuració.
        :return:
        """

        # Accedim a la url i guardem el contingut en local per no haver de tornar a accedir

        url = 'https://www.ecccomics.com/'

        #r = requests.get(url)
        #print(r.content[:100])

        #self.save_html(r.content, 'data/ecccomics')
        html = self.open_html('data/ecccomics')

        # BeautifulSoup

        soup = BeautifulSoup(html, 'html.parser')

        catalog = soup.select("ul li")
        #print(catalog)

        categories = [category.text.strip() for category in catalog]
        #print(categories)

        a_tags = [category.select_one('a') for category in catalog]
        links = [a_tag['href'] if a_tag != None else "" for a_tag in a_tags]

        print(links)



