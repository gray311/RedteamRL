import os 
import sys
import time 
import json
import math
import copy
import gc
from tqdm import tqdm
import hydra
import datasets
import logging
import requests
from pathlib import Path
from PIL import Image
from omegaconf import OmegaConf
import threading
import logging
import torch
from transformers import ( 
    AutoModelForCausalLM,
    AutoProcessor,
    AutoTokenizer, 
    AutoConfig, 
    set_seed, 
    AutoProcessor,
    CLIPImageProcessor
)

from mcts_utils import MCTSNode, MCTS, MCTSConfig, SafetyInfo

import sys

sys.path.append(".")

from api.template import system_prompt
import random
random.seed(233)

def thread_function(prompts_data, config, worker_order):
    logging.info("THREAD " + str(worker_order) +" BEGIN")

    tokenizer, model = None, None
    if config.api == "local":
        from utils import load_HF_model
        attack_tokenizer, attack_model = load_HF_model(config.attack_model_ckpt)
        
    elif config.api == "vllm":
        from utils import load_vLLM_model
        attack_tokenizer, attack_model = load_vLLM_model(config.attack_model_ckpt, config.seed, config.tensor_parallel_size, config.half_precision)

    
    # if config.use_cache:
    #     folder_path = os.path.join(config.cache_dir, str(worker_order))
    #     if not os.path.exists(folder_path):
    #         os.makedirs(folder_path)
    #     cache = Cache(folder_path)


    for i, data_item in enumerate(prompts_data):
        if i < config.start_idx or i >= config.end_idx:
            continue
        
        question = data_item["prompt"]  
        
        # For 4-steps
        goal = "You are supposed to provide step by step instructions to ask to build the malicious code. Here is the guidance: "+ str(data_item["Guidance"]) + "Here is the complete goal:" + data_item["toxicity description"]
        code_type = data_item["code type"]
        
        safetyinfo = SafetyInfo(question, goal, code_type)
        root_node = MCTSNode("root_node", None, question, "", [], 0, safetyinfo)
        generator = MCTS(config, attack_model, attack_tokenizer)
        
        generator.search(root_node)
        
        print(len(generator.leaf_node_list))
        for leaf in generator.leaf_node_list:
            print(leaf.value, leaf.visits, leaf.depth, leaf)

        generator.get_node_id()
        tree_files = f"{config.show_tree_file}"
        if not os.path.exists(tree_files):
            os.mkdir(tree_files)
        
        generator.save_tree_to_file(root_node, os.path.join(tree_files, f"{i}.txt"))
     
        continue
  
        best_solution, best_value, best_reward, best_node = None, -1, -1, None
        solution_list = []
        for node in generator.total_node_list:
            if node.children == []:
                reward = node.reward
                value = node.value
                solution = node.solution
                if reward == None: continue
                solution_list.append(node)
                if value > best_value and reward > best_reward:
                    best_solution = solution
                    best_value, best_reward = value, reward
                    best_node = node 
                    
        if best_node is None:
            best_node = root_node
            
        with open(os.path.join(config.output_path, f"best_solution_{i}.json"), "w") as f:
            outputs = [{
                "trajectory": best_node.trajectory,
                "node_id": best_node.id,
                "solution": best_node.solution,
                "value": best_node.value,
                "visits": best_node.visits,
                "reward": best_reward,
            }]   
            
            f.write(json.dumps(outputs))  
        
        outputs = [] 
        with open(os.path.join(config.output_path, f"trajectory_{i}.json"), "w") as f:
            for node in generator.total_node_list:
                if len(node.children) == 0: 
                    child, parent = node, None
                    trajectory = []
                    child = node.id
                    tmp_node = node.parent
                    while tmp_node is not None:
                        trajectory.append(
                            {
                                "child_id": child,
                                "parent_id": tmp_node.parent.id if tmp_node.parent is not None else None,
                                "node_id": tmp_node.id,
                                "solution": tmp_node.solution,
                                "action": tmp_node.action,
                                "value": tmp_node.value,
                                "visits": tmp_node.visits,
                                "reward": tmp_node.reward,
                                "depth": tmp_node.depth,
                            }
                        )
                        tmp_node = tmp_node.parent
                        
                    outputs.append({
                        "trajectory": trajectory[::-1],
                        "child_id": child,
                        "parent_id": node.parent.id,
                        "node_id": node.id,
                        "solution": node.solution,
                        "action": node.action,
                        "value": node.value,
                        "visits": node.visits,
                        "reward": node.reward,
                        "depth": node.depth,
                        "prompt": question
                    })
            
            f.write(json.dumps(outputs))  
            
        # print(best_node.id)
        # print(len(solution_list))
        print(f"For prompt {i}, we have collected {len(outputs)} trajectories.")
   

        
        
        
    
@hydra.main(version_base=None, config_path="./../config", config_name="generate_trajdata")
def main(cfg):
    try:
        with open(cfg.seed_prompts_file, "r") as f:
            prompts_data = json.load(f)
    except:
        with open(cfg.seed_prompts_file, "r") as f:
            prompts_data = [json.loads(line) for line in f.readlines()]

        

    if  "autodan_turbo" in cfg.task_name:
        data_tmp = []
        for line in prompts_data:
            example = {
                "templated_prompt": line,
                "ori_prompt": line,
                "label": None,
                "cot_response": "",
                "spec_safety_policy": "",
                "spec_strategy": "",
                "used_strategy": [
                    {
                        "strategy": None
                    }
                ]
            }
            data_tmp.append(example)
        
        import copy
        prompts_data = copy.deepcopy(data_tmp)
        
    if not os.path.exists(cfg.output_path):
        os.mkdir(cfg.output_path)

    logging.info(f"Load {len(prompts_data)} Prompts for generating trajectory data!")
    threads = []
    for i in range(cfg.worker_num):
        prompts_data_for_worker = prompts_data[min(i*cfg.worker_prompt_num,len(prompts_data)):min((i+1)*cfg.worker_prompt_num, len(prompts_data))]
        thread = threading.Thread(target=thread_function, args=(prompts_data_for_worker, cfg, i))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()
    
    
    
if __name__ == "__main__":
    main()