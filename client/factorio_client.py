import os
from glob import glob
from itertools import chain
from pathlib import Path
from typing import List

import luadata

from rcon import factorio_rcon
from timeit import default_timer as timer
from slpp import slpp as lua

class FactorioClient:

    def __init__(self, remote_address=None, remote_password=None):
        try:
            self.rcon_client = factorio_rcon.RCONClient('localhost', 27015, "factorio")
            print("Connected to local client.")
        except:
            self.rcon_client = factorio_rcon.RCONClient(remote_address, 27015, remote_password)
            print("Connected to remote client.")

        self.script_dict = {**self._load_actions(), **self._load_init()}

    def _load_scripts(self, scripts):
        script_dict = {}
        for filename in scripts:
            with open(filename, "r") as file:
                script_string = "".join(file.readlines())
                pruned = Path(filename).name[:-4]
                script_dict[pruned] = script_string
        return script_dict

    def _load_actions(self):
        actions = list(chain.from_iterable(glob(os.path.join(x[0], '*.lua')) for x in os.walk('actions')))
        return self._load_scripts(actions)

    def _load_init(self):
        init = list(chain.from_iterable(glob(os.path.join(x[0], '*.lua')) for x in os.walk('init')))
        return self._load_scripts(init)

    def _get_command(self, file, parameters=[], measured=True):
        prefix = "/c " if not measured else '/command '
        script = prefix + self.script_dict[file]
        for index in range(len(parameters)):
            script = script.replace(f"arg{index + 1}", str(parameters[index]))

        return script

    def send(self, command, *parameters, trace=False) -> List[str]:
        script = self._get_command(command, parameters=list(parameters), measured=False)
        start = timer()
        response = self.rcon_client.send_command(script)

        #print(command, parameters, response)
        if response:
            end = timer()
            diff = (end - start)
            splitted = response.split("\n")
            output = lua.decode(splitted[-1])

            ##output = luadata.unserialize(splitted[-1], encoding="utf-8", multival=False)

            if trace:
                print("{hbar}\nCOMMAND: {command}\nPARAMETERS: {parameters}\n\n{response}\n\nOUTPUT:{output}"
                      .format(hbar="-"*100, command=command, parameters=parameters, response=response, output=output))

                # Only the last transmission is considered the output - the rest are just messages
            return output, diff
        end = timer()
        diff = (end - start)
        return lua.decode(response) , diff
