import os
from contextlib import suppress
from operator import attrgetter
from pathlib import Path

from bs4 import BeautifulSoup
from markdown import markdown

from models import Article

articles = Path(__file__).parent / "articles"
articles.mkdir(exist_ok=True)


def article_name_to_file_name(aname: str) -> str:
    return aname.replace(" ", "_") + ".md"


def save_article(article: Article) -> int:
    amount_articles = len(os.listdir(articles))
    with open(articles / f"{amount_articles}.json", "w+") as fout:
        print(article.json(), file=fout)
    return amount_articles


def get_article(article_num: int) -> Article:
    with suppress(FileNotFoundError):
        with open(articles / f"{article_num}.json", "r") as fin:
            return Article.parse_raw(fin.read())
    return Article(title="Not found", body="may guapo luke guide you")


def get_html_article(article_num: int) -> str:
    article = get_article(article_num)
    html_body = __remove_tag(
        __center_images(markdown(article.body, extensions=["extra"])), "h1"
    )
    return f"""
    <html>
        <head>
            <meta charset="UTF-8" />
            <meta name="viewport" content="width=device-width,initial-scale=1">
            <title>{article.title} - ALSWiki</title>
            <link rel="stylesheet" href="https://alswiki.github.io/index.css" />
        </head>
        <body>
            <main class="md">
                <div class="article">
                    <h1>{article.title}</h1>
                    {html_body}
                </div>
            </main>
        </body>
    </html>
    """


def __center_images(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for p in map(attrgetter("parent"), soup.select("p > img")):
        p["align"] = "center"
    return str(soup)


def __remove_tag(html: str, tag: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for el in soup.select(tag):
        el.replace_with("")
    return str(soup)
