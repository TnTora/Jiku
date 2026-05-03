from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .routers import texthooker, books

from pathlib import Path
from os import getenv

config_base = getenv("APPDATA") or getenv("XDG_CONFIG_HOME") or "~/.config"
config_path = Path(config_base).expanduser() / "jiku"
config_path.mkdir(parents=True, exist_ok=True)

books_path = config_path / "books"
books_path.mkdir(exist_ok=True)

app = FastAPI()

app.mount("/static/books", StaticFiles(directory=books_path), name="static-books")

app.include_router(texthooker.router, prefix="/texthooker")
app.include_router(books.router, prefix="/books")

origins = ["http://localhost:5173"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


