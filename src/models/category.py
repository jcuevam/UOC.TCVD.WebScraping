class Category:
    def __init__(self, name, series):
        self.name = name.replace("/", "-") \
            .replace(":", "-") \
            .replace("?", "") \
            .replace("¿", "") \
            .replace("!", "") \
            .replace("¡", "") \
            .replace("\"", "''") \
            .replace("|", "''")
        self.series = series
