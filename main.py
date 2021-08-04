# main.py

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Data(BaseModel):
    msg: str

@app.post("/")
def handle_post(data: Data):
    return data