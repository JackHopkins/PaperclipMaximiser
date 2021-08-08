# main.py

from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.responses import PlainTextResponse

app = FastAPI()

class Data(BaseModel):
    msg: str

@app.get("/healthz")
def healthz():
    return PlainTextResponse("ok")

@app.post("/")
def handle_post(data: Data):
    return data