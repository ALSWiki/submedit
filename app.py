import io
import os
from functools import partial

from aiohttp import ClientSession
from auth import is_authenticated
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, StreamingResponse

from core import article_name_to_file_name, get_article, get_html_article, save_article
from models import Article
from send import GMAIL

assert all(
    map(os.environ.get, ["SENDER_EMAIL", "SENDER_PASSWORD", "GUAPO_EMAIL"])
), "Please specify SENDER_EMAIL, SENDER_PASSWORD, GUAPO_EMAIL env vars"

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def create_sender() -> None:
    email = GMAIL(os.environ["SENDER_EMAIL"], os.environ["SENDER_PASSWORD"])
    app.submit_article = partial(email.send_message, os.environ["GUAPO_EMAIL"])


@app.on_event("startup")
def create_http_session() -> None:
    app.session = ClientSession()


@app.on_event("shutdown")
async def close_http_session() -> None:
    await app.session.close()


@app.get("/preview", response_class=HTMLResponse)
def preview(article: int):
    return HTMLResponse(get_html_article(article))


@app.get("/download")
def download(article: int):
    article = get_article(article)
    response = StreamingResponse(io.StringIO(article.body), media_type="text/markdown")
    fname = article_name_to_file_name(article.title)
    response.headers["Content-Disposition"] = f"attachment; filename={fname}"
    return response


@app.post("/article")
def upload_article(article: Article):
    print("Got article", article.body)
    num = save_article(article)
    subject = f"Article creation/change request: {article.title}"
    body = f"""
    Preview: https://submedit.r2dev2bb8.repl.co/preview?article={num}
    Download: https://submedit.r2dev2bb8.repl.co/download?article={num}
    """
    app.submit_article(subject, body)
    return 200


@app.get("/")
def index():
    return "Submedit api"
