# main.py
import os
from glob import glob
from itertools import chain

import fastapi.responses
from factorio_rcon import factorio_rcon
from fastapi import FastAPI, requests
from pydantic import BaseModel
from fastapi.responses import PlainTextResponse
from starlette.responses import JSONResponse

rcon_client = factorio_rcon.RCONClient("ingressgateway-apis.istio-system.svc.cluster.local/factorio-container", 27015, "factorio")#"eSei2keed0aegai")

character = "players[1]"

script_dict = {}

actions = list(chain.from_iterable(glob(os.path.join(x[0], '*.lua')) for x in
                                   os.walk('actions')))  # [file.split(".")[0] for file in os.listdir('actions')]

for filename in actions:
    with open(filename, "r") as file:
        script_string = "\n".join(file.readlines())
        pruned = filename[8:-4].replace("init/", "")
        script_dict[pruned] = script_string

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
    give_item = send('give_item', parameters=["iron-plate", 1000])
    count = send('count', parameters=['iron-plate'])
    sanity = send('print')
    return JSONResponse({
        "give": give_item,
        "count": count,
        "sanity": sanity
    })

def get_command(file, parameters=[]):
    script = "/c " + script_dict[file]
    for index in range(len(parameters)):
        script = script.replace(f"arg{index+1}", str(parameters[index]))
    return script

def send(command, parameters=[]):
    response = rcon_client.send_command(get_command(command, parameters=parameters)).split("\n")
    print(response)
    return response