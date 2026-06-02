from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from api.core.config import config_path
from api.db import Base, engine
from api.routers import texthooker, books

################ Logging Setup ###########################################################

import logging

logger = logging.getLogger("app_logger")
logger.setLevel(logging.DEBUG)

log_path = config_path / "last_run.log"
fh = logging.FileHandler(str(log_path), mode="w")
fh.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.INFO)

formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
fh.setFormatter(formatter)
ch.setFormatter(formatter)

logger.addHandler(fh)
logger.addHandler(ch)

##########################################################################################

books_path = config_path / "books"
books_path.mkdir(exist_ok=True)

Base.metadata.create_all(engine)

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


