import os
from functools import partial

from fastapi import FastAPI

from models import Article
from send import GMAIL


assert all(map(os.environ.get, ["SENDER_EMAIL", "SENDER_PASSWORD", "GUAPO_EMAIL"])), "Please specify SENDER_EMAIL, SENDER_PASSWORD, GUAPO_EMAIL env vars"

app = FastAPI()

@app.on_event("startup")
def create_sender() -> None:
    email = GMAIL(os.environ["SENDER_EMAIL"], os.environ["SENDER_PASSWORD"])
    app.submit_article = partial(email.send_message, os.environ["GUAPO_EMAIL"])


@app.post("/article")
def upload_article(article: Article):
    subject = f"Article creation/change request: {article.title}"
    app.submit_article(subject, article.body)
    return 200
