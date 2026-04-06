from fastapi import FastAPI
from .routers import texthooker
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.include_router(texthooker.router, prefix="/texthooker")

origins = ["http://localhost:5173"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


