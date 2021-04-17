#watch class for watch_watcher
class Product:
    pass


class Watch(Product):
    def __init__(self, title, price, size, band, water_res, link):
        self.title = title
        self.price = price
        self.size = size
        self.band = band
        self.water_res = water_res
        self.link = link

    def print_product(self):
        print("Title: {}".format(self.title))
        print("Price: ${}".format(self.price))
        print("Size: {}mm".format(self.size))
        print("Band material: {}".format(self.band))
        print("Water resistance: {} m".format(self.water_res))
        print("Link: {}".format(self.link))
        print()


#class that defines cases
class Case(Product):
    def __init__(self, title, model, price, link):
        self.title = title
        self.model = model
        self.price = price
        self.link = link
    
    def print_product(self):
        print("Title: {}".format(self.title))
        print("Model: {}".format(self.model))
        print("Price: ${}".format(self.price))
        print("Link: {}".format(self.link))
        print()

#class that defines straps
class Strap(Product):
    def __init__(self, brand, material, price):
        self.brand = brand
        self.material = material
        self.price = price
