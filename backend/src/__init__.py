from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .http.main import http_router
from .ws.main import ws_router


app = FastAPI() 

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=['*'],
)

app.include_router(http_router, prefix='/app')
app.include_router(ws_router, prefix='/ws')