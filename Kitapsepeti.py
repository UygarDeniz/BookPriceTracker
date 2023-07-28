import requests
from bs4 import BeautifulSoup


class Kitapsepeti:
    def __init__(self, book_title):
        self.book_title = book_title
        self.website_name = "Kitapsepeti.com"
        self.price = None
        self.author = None
        self.publisher = None
        self.book_url = None
        url = f"https://www.kitapsepeti.com/arama?q={self.book_title.replace(' ', '+')}&sort=5"

        response = requests.get(url)
        if response.ok:
            self.soup = BeautifulSoup(response.text, "html.parser")
        else:
            print(response.status_code)

    def get_price(self):
        divs = self.soup.find_all('div',
                                  class_='col col-3 col-md-4 col-sm-6 col-xs-6 p-right mb productItem zoom ease')

        for div in divs:
            a_element = div.find('a', class_='fl col-12 text-description detailLink')

            if a_element and a_element.text.lower().strip() == self.book_title.lower():
                price_div = div.find('div', class_="col col-12 currentPrice")

                self.publisher = div.find("a", class_="col col-12 text-title mt").text
                self.author = div.find("a", class_="fl col-12 text-title").text
                self.book_url = "https://kitapsepeti.com" + a_element["href"]

                if price_div:
                    self.price = float(price_div.text.replace("\n", " ").strip().replace(",", ".").split(" ")[0])
                    break
