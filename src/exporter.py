import csv


class Exporter:

    def __init__(self, csv_name):
        self.csv_name = csv_name
        self.csv_path = "output"
        self.csv_file = f"{self.csv_path}/{csv_name}"
        print("Exporter initialized")

    def get_csv_header(self):
        """
        Retorna el header del csv.

        :return: Llistat de strings amb els títols del header.
        """

        header = ["catalogue",
                  "category",
                  "series",
                  "product_name",
                  "product_description",
                  "product_price",
                  "product_image",
                  "product_availability",
                  "product_original_edition",
                  "product_publishing_date",
                  "product_writer",
                  "product_artist",
                  "product_edition",
                  "product_isbn"]

        return header

    def get_csv_rows(self, catalogues):
        """
        Recorre el nostre dataset per obtenir un llistat de rows pel dataset.

        :param catalogues: Dataset de catàlegs.

        :return: Llistat de rows.
        """

        csv_rows = []

        for catalogue in catalogues:

            for category in catalogue.categories:

                for series in category.series:

                    for product in series.products:

                        row = [catalogue.name,
                               category.name,
                               series.name,
                               product.name,
                               product.description,
                               product.price,
                               product.image,
                               product.availability,
                               product.original_edition,
                               product.publishing_date,
                               product.writer,
                               product.artist,
                               product.edition,
                               product.isbn]

                        csv_rows.append(row)

        return csv_rows

    def export(self, catalogues):
        """
        Exporta el nostre dataset a CSV.

        :param catalogues: Dataset de catàlegs i productes.
        """

        with open(self.csv_file, 'w', encoding="utf-8", newline='') as f:

            print("Exporting...")

            writer = csv.writer(f, delimiter=";")

            header = self.get_csv_header()
            writer.writerow(header)

            rows = self.get_csv_rows(catalogues)
            writer.writerows(rows)

            print("Exported")
