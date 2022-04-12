from scraper import Scraper
from exporter import Exporter

scraper = Scraper(False)
products = scraper.scrape()

exporter = Exporter("ecc_comics_products.csv")
exporter.export(products)
