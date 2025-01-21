import time
from functools import wraps
from typing import Tuple

import numpy
import numpy as np
from PIL import Image as Img
from skimage.util.shape import view_as_windows as viewW

def print_timing(func):
    '''
    create a timing decorator function
    use
    @print_timing
    just above the function you want to time
    '''
    @wraps(func)  # improves debugging
    def wrapper(*arg):
        start = time.perf_counter()  # needs python3.3 or higher
        result = func(*arg)
        end = time.perf_counter()
        fs = '{} took {:.3f} microseconds'
        print(fs.format(func.__name__, (end - start)*1000000))
        return result
    return wrapper

def render_images(factorio):

    for key, val in factorio.minimaps.items():
        data = np.uint8(np.clip(val, 0, 255))
        img = Img.fromarray(data, 'L')
        # img = Image.fromarray(factorio.minimaps['all'], 'RGB')
        img.save(f'logs/{key}.png')
        #img.show()

def stitch(rolled_grid: np.array, added_row: np.array, movement_vector: Tuple[int, int]):
    if movement_vector[0] == 0:
        if movement_vector[1] > 0:
            concatenated = numpy.concatenate([rolled_grid, added_row], axis=0)
            snipped = np.delete(concatenated, 0, 0)
        elif movement_vector[1] < 0:
            concatenated = numpy.concatenate([added_row, rolled_grid], axis=0)
            snipped = np.delete(concatenated, -1, 0)
    elif movement_vector[1] == 0:
        if movement_vector[0] > 0:
            concatenated = numpy.concatenate([rolled_grid, added_row.T], axis=1)
            snipped = np.delete(concatenated, 0, 1)
        elif movement_vector[0] < 0:
            concatenated = numpy.concatenate([added_row.T, rolled_grid], axis=1)
            snipped = np.delete(concatenated, -1, 1)
    else:
        raise Exception("Cannot stitch multiple axes simulateously")

    return snipped

def roll(grid: np.array, movement_vector: Tuple[int, int]):
    # If no X axis movement is happening
    if movement_vector[0] == 0:
        # Roll opposite direction
        return np.roll(grid, movement_vector[1], 0)
        # If no Y axis movement is happening
    elif movement_vector[1] == 0:
        # If both axes are moving
        return np.roll(grid, movement_vector[0], 1)
    else:
        roll_X = np.roll(grid, movement_vector[0], 1)
        return np.roll(roll_X, movement_vector[1], 0)

def strided_indexing_roll(a, r):
    # Concatenate with sliced to cover all rolls
    a_ext = np.concatenate((a, a[:, :-1]), axis=1)

    # Get sliding windows; use advanced-indexing to select appropriate ones
    n = a.shape[1]
    return viewW(a_ext, (1, n))[np.arange(len(r)), (n - r) % n, 0]


def indep_roll(arr, shifts, axis=1):
    """Apply an independent roll for each dimensions of a single axis.

    Parameters
    ----------
    arr : np.ndarray
        Array of any shape.

    shifts : np.ndarray
        How many shifting to use for each dimension. Shape: `(arr.shape[axis],)`.

    axis : int
        Axis along which elements are shifted.
    """
    arr = np.swapaxes(arr,axis,-1)
    all_idcs = np.ogrid[[slice(0,n) for n in arr.shape]]

    # Convert to a positive shift
    shifts[shifts < 0] += arr.shape[-1]
    all_idcs[-1] = all_idcs[-1] - shifts[:, np.newaxis]

    result = arr[tuple(all_idcs)]
    arr = np.swapaxes(result,-1,axis)
    return arr


def eval_program_with_profits(instance, program, profit_config):
        pre_production_flows = instance.get_production_stats()
        # evaluate the step
        try:
            score, goal, result = instance.eval_with_error(program, timeout=300)
            error = False
        except Exception as e:
            result = e
            # get the error message
            result = str(e)
            error = True
        # split result by newlines
        output_list = result.splitlines()
        post_production_flows = instance.get_production_stats()
        profits = get_profits(pre_production_flows, 
                              post_production_flows,
                              profit_config = profit_config)
        return output_list, result, error, profits

def get_unified_production_flows(row, program_lookup):
    meta = row['meta']
    production_input_output_flows ={"input": {}, "output": {}}
    current_objective = None
    while True:
        if "objective" not in meta:
            break
        if meta["objective"] != current_objective:
            input_flows = meta["full_production_flows"]["input"]
            output_flows = meta["full_production_flows"]["output"]
            for item, value in input_flows.items():
                if item in production_input_output_flows["input"]:
                    production_input_output_flows["input"][item] += value
                else:
                    production_input_output_flows["input"][item] = value
            for item, value in output_flows.items():
                if item in production_input_output_flows["output"]:
                    production_input_output_flows["output"][item] += value
                else:
                    production_input_output_flows["output"][item] = value
            current_objective = meta["objective"]

        parent_id = row["parent_id"]
        if parent_id is None:
            break
        row = program_lookup[parent_id]
        meta = row['meta']
    return production_input_output_flows

def get_profits(pre_production_flows, 
                post_production_flows,
                profit_config = {"max_static_unit_profit_cap": 20,
                                 "dynamic_profit_multiplier": 10}):
        """
        Calculate the dynamic production flows between two states
        """
        max_static_unit_profit_cap = profit_config["max_static_unit_profit_cap"]
        dynamic_profit_multiplier = profit_config["dynamic_profit_multiplier"]
        total_profits = {}
        if not isinstance(pre_production_flows, dict) or not isinstance(post_production_flows, dict):
            return total_profits
        if "output" not in pre_production_flows or "output" not in post_production_flows:
            return total_profits
        if isinstance(pre_production_flows["crafted"], dict):
            pre_production_flows["crafted"] = [item for item in pre_production_flows["crafted"].values()]
        if isinstance(post_production_flows["crafted"], dict):
            post_production_flows["crafted"] = [item for item in post_production_flows["crafted"].values()]
        new_production_flows = get_new_production_flows(pre_production_flows, post_production_flows)
        # merge the crafted and harvested dicts to one dict
        static_profits, new_production_flows = get_static_profits(new_production_flows, 
                                                                  pre_production_flows["price_list"],
                                                                  max_craft_cap = max_static_unit_profit_cap) 
        total_profits["static"] = static_profits
        dynamic_profits= get_dynamic_profits(new_production_flows, 
                                                                    pre_production_flows["price_list"],
                                                                    dynamic_profit_multiplier = dynamic_profit_multiplier)
        total_profits["dynamic"] = dynamic_profits
        total_profits["total"] = static_profits + dynamic_profits
        return total_profits

def get_new_production_flows(pre_production_flows, post_production_flows):
    new_production_flows = {
        "input": {},
        "output": {},
        "crafted": [],
        "harvested": {},
    }
    for flow_key in ["input", "output", "harvested"]:
        for item, value in post_production_flows[flow_key].items():
            pre_item_value = pre_production_flows[flow_key][item] if item in pre_production_flows[flow_key] else 0
            diff = value - pre_item_value
            if diff > 0:
                new_production_flows[flow_key][item] = diff
    for item in post_production_flows["crafted"]:
        if item in pre_production_flows["crafted"]:
            # pop the item from the pre_production_flows
            pre_production_flows["crafted"].remove(item)
        else:
            new_production_flows["crafted"].append(item)
    return new_production_flows

def get_static_profits(new_production_flows, price_list, max_craft_cap = 5):
    static_profits = 0
    # first pop all harvested from outputs
    for item, value in new_production_flows["harvested"].items():
        if item in new_production_flows["output"]:
            new_production_flows["output"][item] -= value
            # if the item in input has a 0 value, we can remove it
            if new_production_flows["output"][item] == 0:
                new_production_flows["output"].pop(item)
    # then calculate the profits for each crafted item
    for crafted_item in new_production_flows["crafted"]:
        unit_craft_profit = 0
        count = crafted_item["crafted_count"]
        # first add output value per unit
        for output_item, output_value in crafted_item["outputs"].items():
            item_value = price_list[output_item] if output_item in price_list else 0
            unit_craft_profit += output_value/count * item_value
            # remove the output from the output list
            if output_item in new_production_flows["output"]:
                new_production_flows["output"][output_item] -= output_value
                if new_production_flows["output"][output_item] == 0:
                    new_production_flows["output"].pop(output_item)
        # then subtract input value per unit
        for input_item, input_value in crafted_item["inputs"].items():
            item_value = price_list[input_item] if input_item in price_list else 0
            unit_craft_profit -= input_value/count * item_value
            # remove the input from the input list
            if input_item in new_production_flows["input"]:
                new_production_flows["input"][input_item] -= input_value
                if new_production_flows["input"][input_item] == 0:
                    new_production_flows["input"].pop(input_item)
        # add the unit profit to the static profits
        # we cap the max profit to max_craft_cap items to prevent reward hacking with crafting many items
        static_profits += unit_craft_profit * min(max_craft_cap, count) if max_craft_cap > 0 else unit_craft_profit * count
    return static_profits, new_production_flows


def get_dynamic_profits(new_production_flows, price_list, dynamic_profit_multiplier = 10):
    dynamic_profits = 0
    
    # add the value of all items in output in new_production_flows
        
    for output_item, output_value in new_production_flows["output"].items():
        item_value = price_list[output_item] if output_item in price_list else 0
        dynamic_profits += output_value * item_value
    # take away the value of all items in input in new_production_flows
    # this gets us the dynamic profit
    for input_item, input_value in new_production_flows["input"].items():
        item_value = price_list[input_item] if input_item in price_list else 0
        dynamic_profits -= input_value * item_value
    # multiply the dynamic profit with the dynamic profit multiplier
    dynamic_profits *= dynamic_profit_multiplier
    return dynamic_profits

def eval_program_with_achievements(instance, program):
        pre_production_flows = instance.namespace.get_production_stats()
        # evaluate the step
        try:
            score, goal, result = instance.eval(program, timeout=300)
            error = False
        except Exception as e:
            result = e
            # get the error message
            result = str(e)
            error = True
        # split result by newlines
        output_list = result.splitlines()
        post_production_flows = instance.namespace.get_production_stats()
        achievements = get_achievements(pre_production_flows, post_production_flows)
        return output_list, result, error, achievements

def get_achievements(pre_production_flows, post_production_flows):
        """
        Calculate the dynamic production flows between two states
        """
        achievements = {"static": {}, "dynamic": {}}
        if not isinstance(pre_production_flows, dict) or not isinstance(post_production_flows, dict):
            return achievements
        if "output" not in pre_production_flows or "output" not in post_production_flows:
            return achievements
        
        # merge the crafted and harvested dicts to one dict
        post_production_flows["static_items"] = get_updated_static_items(pre_production_flows, post_production_flows)
        
        achievements = process_achievements(pre_production_flows, post_production_flows, achievements)
        return achievements

def get_updated_static_items(pre_production_flows, post_production_flows):
    if isinstance(pre_production_flows["crafted"], dict):
        pre_production_flows["crafted"] = [item for item in pre_production_flows["crafted"].values()]
    if isinstance(post_production_flows["crafted"], dict):
        post_production_flows["crafted"] = [item for item in post_production_flows["crafted"].values()]
    new_production_flows = get_new_production_flows(pre_production_flows, post_production_flows)
    static_items = new_production_flows["harvested"]
    
    for item in new_production_flows["crafted"]:
        output = item["outputs"]
        for key, value in output.items():
            if key in static_items:
                static_items[key] += value
            else:
                static_items[key] = value
    return static_items

def process_achievements(pre_sleep_production_flows, post_sleep_production_flows, achievements):
    for item_key in post_sleep_production_flows["output"]:
        post_output_value = post_sleep_production_flows["output"][item_key]
        pre_output_value = pre_sleep_production_flows["output"][item_key] if item_key in pre_sleep_production_flows["output"] else 0
        # check if new items have been created
        if post_output_value > pre_output_value:
            created_value = post_output_value - pre_output_value
            # We need to look if its dynamic or static added value
            # if static greater than 0, we add it to static
            # we add the rest to dynamic
            static_value = post_sleep_production_flows["static_items"][item_key] if item_key in post_sleep_production_flows["static_items"] else 0
            if static_value > 0:
                achievements["static"][item_key] = static_value
            if created_value > static_value:
                achievements["dynamic"][item_key] = created_value - static_value
    return achievements