
class Shelf:
    def __init__(self):
        self.items = []

    def put(self, item):
        self.items.append(item)

    def show(self):
        for item in self.items:
            print(item)

class Book:
    def __init__(self, title, pages):
        self.title = title
        self.pages = pages

    def __repr__(self):
        return f'<Book "{self.title}">'

    def __len__(self):
        return pages


shelf = Shelf()
book1 = Book("Ulysses", 272)
book2 = Book("Hamlet", 342)

shelf.put(book1)
shelf.put(book2)

peep(shelf)

shelf.show()
