class Catalogue:

    def __init__(self, name, link, categories):
        self.name = name.replace("/", "-") \
            .replace(":", "-") \
            .replace("?", "") \
            .replace("¿", "") \
            .replace("!", "") \
            .replace("¡", "") \
            .replace("\"", "''") \
            .replace("|", "''")
        self.link = link
        self.categories = categories
