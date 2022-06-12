import os
from glob import glob
from itertools import chain
from pathlib import Path
from typing import List
from factorio_rcon import AsyncRCONClient
from timeit import default_timer as timer
from slpp import slpp as lua



def _load_scripts(scripts):
    script_dict = {}
    for filename in scripts:
        with open(filename, "r") as file:
            script_string = "".join(file.readlines())
            pruned = Path(filename).name[:-4]
            script_dict[pruned] = script_string
    return script_dict

def _load_actions():
    actions = list(chain.from_iterable(glob(os.path.join(x[0], '*.lua')) for x in os.walk('client/actions')))
    return _load_scripts(actions)

def _load_init():
    init = list(chain.from_iterable(glob(os.path.join(x[0], '*.lua')) for x in os.walk('client/init')))
    return _load_scripts(init)



def _lua2python(command, response, *parameters, trace=False, start=0):
    if trace:
        print(command, parameters, response)
    if response:
        if trace:
            print(f"success: {command}")
        end = timer()
        splitted = response.split("\n")
        output = lua.decode(splitted[-1])

        ##output = luadata.unserialize(splitted[-1], encoding="utf-8", multival=False)

        if trace:
            print("{hbar}\nCOMMAND: {command}\nPARAMETERS: {parameters}\n\n{response}\n\nOUTPUT:{output}"
                  .format(hbar="-" * 100, command=command, parameters=parameters, response=response, output=output))

            # Only the last transmission is considered the output - the rest are just messages
        return output, (end - start)
    else:
        if trace:
            print(f"failure: {command} \t")
    end = timer()
    return lua.decode(response), (end - start)

