import requests
from bs4 import BeautifulSoup

from src.models.catalogue import Catalogue
from src.models.category import Category
from src.models.product import Product
from src.models.series import Series


class Scraper:
    const_comics_root = "/comics/"
    const_extra_info_separator = "||"
    const_original_edition = "EDICIÓN ORIGINAL"
    const_publishing_date = "FECHA PUBLICACIÓN"
    const_publishing_date_2 = "FECHA SALIDA"
    const_writer = "GUIÓN"
    const_artist = "DIBUJO"
    const_edition = "FORMATO"
    const_edition_2 = "MEDIDAS"
    const_isbn = "ISBN"
    const_isbn_2 = "REFERENCIA"

    def __init__(self):
        self.catalogues = []
        print("Scraper inicialitzat")

    def request_html(self, url):
        print(f"Scraping: {url}")
        return requests.get(url)

    def save_html(self, html, file_name):
        with open(f"data/{file_name}", 'wb') as f:
            f.write(html)

    def open_html(self, file_name):
        with open(f"data/{file_name}", 'rb') as f:
            return f.read()

    def scrape_catalogues(self, html):
        soup = BeautifulSoup(html, 'html.parser')

        # Agafem tots els li dintre de ul
        catalogue_entries = soup.select("ul li")

        # Ens quedem amb els links
        a_tags = [catalogue_entry.select_one('a') for catalogue_entry in catalogue_entries]
        catalogue_links = [a_tag['href']
                           for a_tag
                           in a_tags
                           if a_tag is not None
                           and self.const_comics_root in a_tag['href']][23:]

        # Agafem els noms que tenen
        catalogue_names = [entry.text.strip()
                           for a_tag, entry
                           in zip(a_tags, catalogue_entries)
                           if a_tag is not None
                           and self.const_comics_root in a_tag['href']][23:]

        # Fem la request dels documents que tindrem
        # htmls = [self.request_html(link) for link in catalogue_links]

        for name, link in zip(catalogue_names, catalogue_links):
            self.catalogues.append(Catalogue(name, link, []))
            # self.save_html(html.content, name)

    def scrape_comics_links_and_names(self, link, name, index):
        """
        Funció recursiva per obtenir tots els links a cómics seguint la paginació.

        :param link: Link de la pàgina (paginada)
        :param name: Nom de la sèrie a la que pertany
        :param index: Paginació (0-based).

        :return:Llistat de links a comics.
        """

        name_page = f"{name}_{index}"
        index += 1

        r = self.request_html(link)
        html = r.content
        self.save_html(html, name_page)

        html = self.open_html(name_page)

        soup = BeautifulSoup(html, 'html.parser')

        comics_list = soup.select_one(".lstprod")
        comics_a_tags = comics_list.select(".titprod > a")
        comics_links = [a_tag["href"] for a_tag in comics_a_tags]
        comics_names = [a_tag.text.strip().replace("/", "-") \
                            .replace(":", "-") \
                            .replace("?", "") \
                            .replace("¿", "") \
                            .replace("!", "") \
                            .replace("¡", "") \
                            .replace("\"", "''") \
                            .replace("|", "''") for a_tag in comics_a_tags]

        pagination_right = soup.select_one(".pagination > .right")

        if pagination_right is not None:

            pagination_right_a_tag = pagination_right.select_one("a")

            if pagination_right_a_tag.has_attr("href"):

                pagination_right_link = pagination_right_a_tag["href"]

                if pagination_right_link != "":

                    links, names = self.scrape_comics_links_and_names(pagination_right_link, name, index)

                    for link, name in zip(links, names):
                        comics_links.append(link)
                        comics_names.append(name)

        return comics_links, comics_names

    def parse_extra_comic_information(self, extra_data_txt):

        extra_data = extra_data_txt.split(self.const_extra_info_separator)

        original_edition = ""
        publishing_date = ""
        writer = ""
        artist = ""
        edition = ""
        isbn = ""

        for data in extra_data:

            if self.const_original_edition in data:
                original_edition = data.split(self.const_original_edition)[-1].split(":", 1)[-1].strip()
            elif self.const_publishing_date in data:
                publishing_date = data.split(self.const_publishing_date)[-1].split(":", 1)[-1].strip()
            elif self.const_publishing_date_2 in data:
                publishing_date = data.split(self.const_publishing_date_2)[-1].split(":", 1)[-1].strip()
            elif self.const_writer in data:
                writer = data.split(self.const_writer)[-1].split(":", 1)[-1].strip()
            elif self.const_artist in data:
                artist = data.split(self.const_artist)[-1].split(":", 1)[-1].strip()
            elif self.const_edition in data:
                edition = data.split(self.const_edition)[-1].split(":", 1)[-1].strip()
            elif self.const_edition_2 in data:
                edition = data.split(self.const_edition_2)[-1].split(":", 1)[-1].strip()
            elif self.const_isbn in data:
                isbn = data.split(self.const_isbn)[-1].split(":", 1)[-1].strip()
            elif self.const_isbn_2 in data:
                isbn = data.split(self.const_isbn_2)[-1].split(":", 1)[-1].strip()

        return original_edition, publishing_date, writer, artist, edition, isbn

    def scrape_comic(self, link, name):

        r = self.request_html(link)
        html = r.content
        self.save_html(html, name)

        html = self.open_html(name)

        soup = BeautifulSoup(html, 'html.parser')

        # Camps que podem extreure directament
        title = soup.select_one(".titprod").text.strip()
        description = soup.select_one(".txtprod").text.strip().strip()
        price = soup.select_one(".precio").text.strip()
        image = soup.select_one(".imgprod").select_one("a")["href"]

        # Agafem botó de comprar per veure disponibilitat
        btn_buy = soup.select_one(".botoncomprar")
        if btn_buy is None:
            availability = False
        else:
            availability = True

        # Aquesta informació l'haurem de parsejar i transformar en altres camps
        extra_data = soup.select_one(".infoprod").text.strip()
        original_edition, publishing_date, writer, artist, edition, isbn = self.parse_extra_comic_information(
            extra_data)

        return Product(name,
                     description,
                     price,
                     image,
                     availability,
                     original_edition,
                     publishing_date,
                     writer,
                     artist,
                     edition,
                     isbn)

    def scrape_comics(self, series):

        comics = []

        link = series.link
        name = series.name

        # Agafem tots els comics

        # Crida a la funció recursiva que ens retorna tots els links a comics

        comics_links, comics_names = self.scrape_comics_links_and_names(link, name, 0)

        print(comics_links)
        print(comics_names)

        for comic_link, comic_name in zip(comics_links, comics_names):
            comics.append(self.scrape_comic(comic_link, comic_name))

        return comics

    def scrape_categories_and_series(self):

        for catalogue in self.catalogues:

            link = catalogue.link
            name = catalogue.name

            # r = self.request_html(link)
            # html = r.content
            # self.save_html(html, name)

            html = self.open_html(name)

            soup = BeautifulSoup(html, 'html.parser')

            # Agafem les categories i el llistat de series de cada categoria
            category_names = [category.text.strip() for category in soup.select(".tit-cat")]
            series_lists = [category for category in soup.select("div > .subcat")]

            categories = [Category(category, []) for category in category_names]

            for category, series_list in zip(categories, series_lists):

                series_a_tags = series_list.select("a")
                series_links = [a_tag["href"] for a_tag in series_a_tags]
                series_names = [a_tag.text.strip() for a_tag in series_a_tags]

                category.series = [Series(name, link, []) for name, link in zip(series_names, series_links)]

                for series in category.series:
                    comics = self.scrape_comics(series)
                    series.comics = comics

            catalogue.categories = categories

            print(categories)

    def scrape(self):
        """
        Funció main de la nostra classe Scraper.
        :param config: JSON amb els paràmetres de configuració.
        :return:
        """

        # Accedim a la url i guardem el contingut en local per no haver de tornar a accedir

        url = 'https://www.ecccomics.com/'
        # r = self.request_html(url)

        # self.save_html(r.content, 'ecccomics')
        html = self.open_html('ecccomics')

        # Scrape catalogues

        self.scrape_catalogues(html)

        self.scrape_categories_and_series()

        print("")
        # for catalogue in catalogues
