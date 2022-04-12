class Series:

    def __init__(self, name, link, products):
        self.name = name.replace("/", "-") \
            .replace(":", "-") \
            .replace("?", "") \
            .replace("¿", "") \
            .replace("!", "") \
            .replace("¡", "") \
            .replace("\"", "''") \
            .replace("|", "''")
        self.link = link
        self.products = products
