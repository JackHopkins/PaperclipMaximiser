from typing import Any
from llm_factory import LLMFactory

class PlanSampler():
    def __init__(self, model, system_prompt_path, starting_scenarios_folder,):
        
        self.model = model
        self.system_prompt_path = system_prompt_path
        self.llm_factory = LLMFactory(model)
        self.starting_scenarios_folder = starting_scenarios_folder
        
    
    def get_unsupervised_objective(self, instance):
        """
        Runs the traces, adds the plan to the prompt and saves the traces to the save path
        """
        starting_inventory = instance.inspect_inventory()
        self.init_system_prompt(instance)
        mining_setup = self.get_mining_setup(instance)
        messages = [{"role": "system", "content": self.system_prompt}]
        user_message = f"Your starting inventory is {starting_inventory}. Your initial mining setup is: {mining_setup}. Create a useful task that you can carry out in the current game and the python script to achieve the task"
        messages.append({"role": "user", "content": user_message})
        response = self.llm_factory.call(messages=messages,
                                         model = self.model,
                                        temperature=0.7,
                                        max_tokens=4096,
                                        stop_sequences = ["\n"])
        
        
        full_output = response.choices[0].message.content
        full_output = full_output.lower().replace("sure! the task i will carry out is", "").strip()
        if "." in full_output:
            full_output = full_output.split(".")[0]
        return full_output
    
    def get_mining_setup(self, instance):
        mining_setup = instance.get_entities()
        if len(mining_setup) == 0:
            mining_setup = "There are no entities on the map"
        else:
            mining_setup = f"The following entities are on the map and can be used: {mining_setup}"
        return mining_setup
    
    def init_system_prompt(self, instance):
        api_description = instance.get_system_prompt()
        system_prompt_path = self.system_prompt_path
        # read in the system prompt
        with open(system_prompt_path, "r") as f:
            system_prompt = f.read()
        self.system_prompt = system_prompt.format(schema=api_description)


    def __call__(self, instance, game_state_str) -> Any:
        instance.reset(game_state_str)
        return self.get_unsupervised_objective(instance)