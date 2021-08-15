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

client = []
# "ingressgateway-apis.istio-system.svc.cluster.local/factorio-container", 27015, "factorio")#"eSei2keed0aegai")

character = "players[1]"

script_dict = {}

actions = list(chain.from_iterable(glob(os.path.join(x[0], '*.lua')) for x in
                                   os.walk('actions')))  # [file.split(".")[0] for file in os.listdir('actions')]
print(actions)

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

@app.get("/load")
def load_actions():
    actions = list(chain.from_iterable(glob(os.path.join(x[0], '*.lua')) for x in
                                       os.walk('actions')))  # [file.split(".")[0] for file in os.listdir('actions')]
    print(actions)

    for filename in actions:
        with open(filename, "r") as file:
            script_string = "\n".join(file.readlines())
            pruned = filename[8:-4].replace("init/", "")
            script_dict[pruned] = script_string

    print(script_dict)


@app.get("/commands")
def handle_commands():
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
        script = script.replace(f"arg{index + 1}", str(parameters[index]))
    return script


def send(command, parameters=[]):
    if len(client) == 0:
        try:
            rcon_client = factorio_rcon.RCONClient("localhost", 27015, "factorio")
        except Exception as e:
            rcon_client = factorio_rcon.RCONClient("localhost", 27015, "default")
            print("Defaulting password. Something is awry.")

        client.append(rcon_client)

    script = get_command(command, parameters=parameters)
    print(script)
    response = client[0].send_command(script)#.split("\n")
    print(response)

    return response
