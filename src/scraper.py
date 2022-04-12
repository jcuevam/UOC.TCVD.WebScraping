import requests
from bs4 import BeautifulSoup
import time

from src.models.catalogue import Catalogue
from src.models.category import Category
from src.models.product import Product
from src.models.series import Series


class Scraper:
    const_comics_root = "/comics/"
    const_recommended_price = "PVP recomendado: "
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

    def __init__(self, download_content):
        self.catalogues = []
        self.url = 'https://www.ecccomics.com/'
        self.download_content = download_content
        print("Scraper initialized")

    def get_html_content(self, url, file_name):
        """
        Funció per accedir a un HTML mitjançant un request o accedint al fitxer local i guardar-ho en local.

        :param url: URL a la que hem d'accedir.
        :param file_name: Nom del fitxer per guardar/llegir.

        :return: Contingut HTML de la pàgina.
        """

        print(f"Accessing: {url}")

        if self.download_content:
            html = self.request_html(url)
            self.save_html(html, file_name)
        else:
            html = self.read_html(file_name)

        return html

    def request_html(self, url):
        """
        Fa una crida a una URL i retorna el seu contingut.
        Té un sleep d'1 segon per no saturar el servidor objectiu.

        :param url: URL a la que fer la crida.

        :return: Content del HTML.
        """

        time.sleep(1)
        return requests.get(url).content

    def save_html(self, html, file_name):
        """
        Guarda el contingut HTML en un fitxer en local.

        :param html: Contingut HTML.
        :param file_name: Nom del fitxer.
        """

        with open(f"data/{file_name}", 'wb') as f:
            f.write(html)

    def read_html(self, file_name):
        """
        Llegeix un fitxer local per agafar contingut HTML.

        :param file_name: Nom del fitxer.

        :return: Contingut HTML del fitxer local.
        """

        with open(f"data/{file_name}", 'rb') as f:
            return f.read()

    def parse_extra_product_information(self, extra_data_txt):
        """
        Funció per pasejar informació extra que ens arriba tota junta en un string.

        :param extra_data_txt: String que conté la informació.

        :return: Strings amb informació extra.
        """

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

    def download_picture(self, link, name):
        """
        Descarrega una imatge amb el seu link si tenim el self.download_content a True.

        :param link: Link a la imatge.
        :param name: Nom de la imatge (producte al que correspon).
        """

        if self.download_content:

            time.sleep(1)
            r = requests.get(link, stream=True)

            if r.status_code == 200:

                file_name = name.replace(".", "") \
                    .replace("/", "-") \
                    .replace(":", "-") \
                    .replace("?", "") \
                    .replace("¿", "") \
                    .replace("!", "") \
                    .replace("¡", "") \
                    .replace("\"", "''") \
                    .replace("|", "''")
                ruta = f"pictures/{file_name}.png"

                output = open(ruta, "wb")

                for chunk in r:
                    output.write(chunk)

                output.close()

    def scrape_product(self, link, name):
        """
        Scrape i emplenar un producte.

        :param link: Link del producte.
        :param name: Nom del producte.

        :return: Producte emplenat.
        """

        print(f"-------- Scraping product: {name}")

        html = self.get_html_content(link, name)

        soup = BeautifulSoup(html, 'html.parser')

        # Camps que podem extreure directament
        title = soup.select_one(".titprod").text.strip()
        description = soup.select_one(".txtprod").text.strip().replace("\t", " ").replace("\r", " ").replace("\n", " ")
        price = float(soup.select_one(".precio")
                      .text
                      .strip()[:-2]
                      .replace(".", "")
                      .replace(",", ".")
                      .replace(self.const_recommended_price, ""))
        image = soup.select_one(".imgprod").select_one("a")["href"]
        self.download_picture(image, title)

        # Agafem botó de comprar per veure disponibilitat
        btn_buy = soup.select_one(".botoncomprar")
        if btn_buy is None:
            availability = False
        else:
            availability = True

        # Aquesta informació l'haurem de parsejar i transformar en altres camps
        extra_data = soup.select_one(".infoprod").text.strip()
        original_edition, publishing_date, writer, artist, edition, isbn = self.parse_extra_product_information(
            extra_data)

        # Retornem el producte
        return Product(title,
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

    def scrape_products_links_and_names(self, link, name, index):
        """
        Funció recursiva per obtenir tots els links a cómics seguint la paginació.

        :param link: Link de la pàgina (paginada)
        :param name: Nom de la sèrie a la que pertany
        :param index: Paginació (0-based).

        :return:Llistat de links a comics.
        """

        name_page = f"{name}_{index}"
        index += 1

        html = self.get_html_content(link, name_page)

        soup = BeautifulSoup(html, 'html.parser')

        # Emplenem els comics de la pàgina
        comics_list = soup.select_one(".lstprod")
        comics_a_tags = comics_list.select(".titprod > a")
        comics_links = [a_tag["href"] for a_tag in comics_a_tags]
        comics_names = [a_tag.text.strip().replace("/", "-")
                            .replace(":", "-")
                            .replace("?", "")
                            .replace("¿", "")
                            .replace("!", "")
                            .replace("¡", "")
                            .replace("\"", "''")
                            .replace("|", "''") for a_tag in comics_a_tags]

        # Cercem si hi ha botó per continuar i seguimt
        pagination_right = soup.select_one(".pagination > .right")

        if pagination_right is not None:

            pagination_right_a_tag = pagination_right.select_one("a")

            if pagination_right_a_tag.has_attr("href"):

                pagination_right_link = pagination_right_a_tag["href"]

                if pagination_right_link != "":

                    links, names = self.scrape_products_links_and_names(pagination_right_link, name, index)

                    # Si hi havia, els afegim al llistat
                    for link, name in zip(links, names):
                        comics_links.append(link)
                        comics_names.append(name)

        return comics_links, comics_names

    def scrape_products(self, series):
        """
        Scrape i emplena els productes d'una sèrie.

        :param series: Serie a la que pertanyen els productes.

        :return: Llistat de productes emplenats.
        """

        comics = []

        link = series.link
        name = series.name

        # Crida a la funció recursiva que ens retorna tots els links a comics
        comics_links, comics_names = self.scrape_products_links_and_names(link, name, 0)

        # Creem els productes
        for comic_link, comic_name in zip(comics_links, comics_names):
            comics.append(self.scrape_product(comic_link, comic_name))

        return comics

    def scrape_categories_and_series(self, catalogue_link, catalogue_name):
        """
        Scrape i emplena les categories d'un catàleg i les sèries de la categoria.
        Fem categoria i sèrie en una mateixa funció perquè es troben a la mateixa pàgina,
        no  existeix una pàgina per les categoríes.

        :param catalogue_link: Link del catàleg al que pertanyen les categories.
        :param catalogue_name: Nom del catàleg al que pertanyen les categories.

        :return: Llistat de categories emplenades.
        """

        html = self.get_html_content(catalogue_link, catalogue_name)

        soup = BeautifulSoup(html, 'html.parser')

        # Agafem les categories i el llistat de series de cada categoria
        category_names = [category.text.strip() for category in soup.select(".tit-cat")]
        series_lists = [category for category in soup.select("div > .subcat")]

        # Creem les categories
        categories = [Category(category, []) for category in category_names]

        for category, series_list in zip(categories, series_lists):

            print(f"---- Scraping category: {category.name}")

            # Obtenim els links a les diferents series
            series_a_tags = series_list.select("a")
            series_links = [a_tag["href"] for a_tag in series_a_tags]
            series_names = [a_tag.text.strip() for a_tag in series_a_tags]

            # Creem les sèries
            category.series = [Series(name, link, []) for name, link in zip(series_names, series_links)]

            # Emplenem els productes de les sèries
            for series in category.series:
                print(f"------ Scraping series: {series.name}")

                products = self.scrape_products(series)
                series.products = products

        return categories

    def scrape_catalogues(self, html):
        """
        Scrape els catàlegs, els omple i els guarda al self.catalogues.

        :param html: Contingut HTML de la pàgina que conté els catàlegs.
        """

        soup = BeautifulSoup(html, 'html.parser')

        # Agafem tots els li dintre de ul
        catalogue_entries = soup.select("ul li")

        # Ens quedem amb els links
        a_tags = [catalogue_entry.select_one('a') for catalogue_entry in catalogue_entries]
        catalogue_links = [a_tag['href']
                           for a_tag
                           in a_tags
                           if a_tag is not None
                           and self.const_comics_root in a_tag['href']]

        # Agafem els noms que tenen
        catalogue_names = [entry.text.strip()
                           for a_tag, entry
                           in zip(a_tags, catalogue_entries)
                           if a_tag is not None
                           and self.const_comics_root in a_tag['href']]

        # Omplim els catàlegs
        for name, link in zip(catalogue_names, catalogue_links):
            print(f"-- Scraping catalogue: {name}")

            categories = self.scrape_categories_and_series(link, name)
            self.catalogues.append(Catalogue(name, link, categories))

    def scrape(self):
        """
        Funció main de la nostra classe Scraper.

        :return: Dataset conformat per un llistat de catàlegs.
        """

        # Accedim a la url i guardem el contingut en local per no haver de tornar a accedir
        html = self.get_html_content(self.url, "ecccomics")

        # Scrape catalogues
        self.scrape_catalogues(html)

        return self.catalogues
