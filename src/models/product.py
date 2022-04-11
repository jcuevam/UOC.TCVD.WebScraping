class Product:

    def __init__(self,
                 name,
                 description,
                 price,
                 image,
                 availability,
                 original_edition,
                 publishing_date,
                 writer,
                 artist,
                 edition,
                 isbn):
        self.name = name.replace("/", "-") \
            .replace(":", "-") \
            .replace("?", "") \
            .replace("¿", "") \
            .replace("!", "") \
            .replace("¡", "") \
            .replace("\"", "''") \
            .replace("|", "''")
        self.description = description
        self.price = price
        self.image = image
        self.availability = availability
        self.original_edition = original_edition
        self.publishing_date = publishing_date
        self.writer = writer
        self.artist = artist
        self.edition = edition
        self.isbn = isbn
