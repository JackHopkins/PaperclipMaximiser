# main.py
import fastapi.responses
from fastapi import FastAPI, requests
from pydantic import BaseModel
from fastapi.responses import PlainTextResponse
from starlette.responses import JSONResponse

from client.app.utils import get_command, client

app = FastAPI()

class Data(BaseModel):
    msg: str

@app.get("/healthz")
def healthz():
    return PlainTextResponse("ok")

@app.post("/msg")
def handle_post(data: Data):
    return data

@app.get("/chain")
def handle_chain():
    give_item = client.send('give_item', parameters=["iron-plate", 1000])
    count = client.send('count', parameters=['iron-plate'])
    sanity = client.send('print')
    return JSONResponse({
        "give": give_item,
        "count": count,
        "sanity": sanity
    })