import requests
from bs4 import BeautifulSoup


class Alternatifkitap:

    def __init__(self, book_title):
        self.book_title = book_title
        self.website_name = "Alternatifkitap.com"
        self.price = None
        self.author = None
        self.publisher = None
        self.book_url = None
        url = f"https://www.alternatifkitap.com/ara/?search_performed=Y&q={self.book_title.replace(' ', '+')}"
        response = requests.get(url)

        if response.ok:
            self.soup = BeautifulSoup(response.text, "html.parser")

        else:
            print(response.status_code)

    def get_price(self):
        divs = self.soup.find_all("div",
                                  class_="ut2-gl__body")
        for div in divs:
            a_element = div.find("a", class_="product-title")
            title_in_element = a_element.text.lower().split("-", 1)[0].strip().lower()

            if a_element and title_in_element == self.book_title.lower():

                if div.find("span", class_="ty-price-num") is not None:
                    self.price = float(div.find("span", class_="ty-price-num").text.split(" ")[0])

                else:
                    self.price = float(div.find("span", class_="ty-price").text.split(" ")[0])

                self.author = a_element.text.split("-")[1]
                self.publisher = a_element.text.split("-")[2]
                self.book_url = "https://www.alternatifkitap.com" + a_element.attrs["href"]
                break
