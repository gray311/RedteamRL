
import json, os, shutil, re, random, io, time
import torch

def tensor_to_bytes(t):
    buffer = io.BytesIO()
    torch.save(t, buffer)
    return buffer.getvalue()
def bytes_to_tensor(b):
    return torch.load(io.BytesIO(b), weights_only=True)
def make_bytes_list(blist):
    buffer = io.BytesIO()
    buffer.write(len(blist).to_bytes(4, 'big'))
    for b in blist:
        buffer.write(len(b).to_bytes(4, 'big'))
        buffer.write(b)
    return buffer.getvalue()
def bytes_list_to_list(b):
    buffer = io.BytesIO(b)
    num = int.from_bytes(buffer.read(4), 'big')
    blist = []
    for _ in range(num):
        l = int.from_bytes(buffer.read(4), 'big')
        blist.append(buffer.read(l))
    return blist


"""
CUDA_VISIBLE_DEVICES=5 python mcts/victim_server.py
"""
if __name__ == '__main__':   
    from transformers import AutoTokenizer, AutoModelForCausalLM
    import torch
    import torch.nn as nn

    from bottle import request
    import bottle, threading, queue
    os.environ['TOKENIZERS_PARALLELISM'] = 'true'

    model_path = "Qwen/Qwen2.5-Coder-7B-Instruct"

    victim_model = AutoModelForCausalLM.from_pretrained(model_path,
            torch_dtype=torch.bfloat16, _attn_implementation="sdpa").to('cuda')
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    victim_model.eval()
    victim_model.requires_grad_(False)


    raw_queue = queue.LifoQueue()
    result_queue = queue.LifoQueue()

    app = bottle.Bottle() 

    @app.route('/upload', method='POST')
    def do_upload():
        try:
            json_data = request.json
            if not all(k in json_data for k in ['prompt', 'answer', 'label', 'step']):
                return {'error': 'Missing parameters'}
        except:
            return {'error': 'Invalid JSON'}
        
        raw_queue.put(json_data)
        return b'tensor'

    @app.route('/get', method='GET')
    def do_get():
        if result_queue.empty(): return b'empty'
        return result_queue.get()
    
    def run_server(): bottle.run(app, host='0.0.0.0', port=59875, server='tornado')
    threading.Thread(target=run_server, daemon=False).start()

    while True:
        data = raw_queue.get()
        prompt = data['prompt']
        system = "You are a AI assistant."
        messages = [{"role": "system", "content": system}, {"role": "user", "content": data['prompt']}]
    
        text = tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )
 
        model_inputs = tokenizer([text], return_tensors="pt").to(victim_model.device)

        generated_ids = victim_model.generate(
            **model_inputs,
            max_new_tokens=1024
        )
        generated_ids = [
            output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
        ]

        outputs = tokenizer.batch_decode(generated_ids)[0].strip("\n")
        
        print(text)
        

        print(outputs)


        result_queue.put(json.dumps({"response": outputs}).encode())