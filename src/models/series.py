class Series:

    def __init__(self, name, link, comics):
        self.name = name.replace("/", "-") \
            .replace(":", "-") \
            .replace("?", "") \
            .replace("¿", "") \
            .replace("!", "") \
            .replace("¡", "") \
            .replace("\"", "''") \
            .replace("|", "''")
        self.link = link
        self.comics = comics
