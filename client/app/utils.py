import os
from glob import glob
from pathlib import Path

import factorio_rcon
from itertools import chain

rcon_client = factorio_rcon.RCONClient("ingressgateway-apis.istio-system.svc.cluster.local/factorio-container", 27015, "eSei2keed0aegai")

character = "players[1]"

script_dict = {}

actions = list(chain.from_iterable(glob(os.path.join(x[0], '*.lua')) for x in
                                   os.walk('actions')))  # [file.split(".")[0] for file in os.listdir('actions')]

for filename in actions:
    with open(filename, "r") as file:
        script_string = "\n".join(file.readlines())
        pruned = filename[8:-4].replace("init/", "")
        script_dict[pruned] = script_string

def get_command(file, parameters=[]):
    script = "/c " + script_dict[file]
    for index in range(len(parameters)):
        script = script.replace(f"arg{index+1}", str(parameters[index]))
    return script

def send(command, parameters=[]):
    response = rcon_client.send_command(get_command(command, parameters=parameters)).split("\n")
    print(response)
    return response