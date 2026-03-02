import csv

import requests
from bs4 import BeautifulSoup, Tag
from dataclasses import dataclass, fields, astuple

BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]
    author_description: str


FIELDS = [field.name for field in fields(Quote)]


def serializer_quote(quote: Tag) -> Quote:
    description_pref = quote.select_one("span>a")["href"]
    res_description = requests.get(BASE_URL + description_pref).content
    description = (BeautifulSoup(res_description, "html.parser")
                   .select_one(".author-description").text)
    return Quote(
        text=quote.select_one(".text").string,
        author=quote.select_one(".author").string,
        tags=[tag.string for tag in quote.select(".tag")],
        author_description=description.strip(),
    )


def scrape_quotes(url: str) -> list[Quote]:
    quotes = []
    response = requests.get(url).content
    soup = BeautifulSoup(response, "html.parser")
    quotes += soup.select(".quote")
    print("/page/1/")
    next_button_pref = soup.select_one("li.next>a")["href"]

    while True:
        print(next_button_pref)
        response = requests.get(BASE_URL + next_button_pref).content
        soup = BeautifulSoup(response, "html.parser")
        quotes += soup.select(".quote")
        next_button = soup.select_one("li.next>a")

        if not next_button:
            break

        next_button_pref = next_button["href"]

    return [serializer_quote(quote) for quote in quotes]


def main(output_csv_path: str) -> None:
    quotes = scrape_quotes(BASE_URL)
    with open(output_csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(FIELDS)
        writer.writerows([astuple(quote) for quote in quotes])


if __name__ == "__main__":
    main("quotes.csv")
