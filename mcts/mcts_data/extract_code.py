# python mcts/mcts_data/extract_code.py 
import re

import os

# 读取原始文件并提取代码块
def extract_and_save_code(txt_file_dict_path,txt_name):
    with open(os.path.join(txt_file_dict_path,txt_name), 'r') as file:
        content = file.read()
    
    # 正则表达式匹配以 "、、、python" 为标记的代码块
    # 这里假设代码块以 '、、、python' 开始，并以 '、、、' 结束
    python_code_blocks = re.findall(r'```python\s*(.*?)\s*```', content, re.DOTALL)
    
    # 保存每个代码块到不同的 Python 文件
    path = file_name = os.path.join(txt_file_dict_path,"code/")
    if not os.path.exists(path):
        os.makedirs(path)
    for idx, code_block in enumerate(python_code_blocks, 1):
        file_name = f'code_{idx}.py'
        file_name = os.path.join(path,file_name)
        with open(file_name, 'w') as code_file:
            cleaned_code_block = code_block.replace("│", "").strip()  # Clean unwanted characters
            # Ensure newlines are properly preserved
            code_file.write(cleaned_code_block)
        print(f'Saved code block {idx} to {file_name}')


txt_file_dict_path = 'mcts/mcts_data/multi_turn_jailbreak/rollout64/trees/'
txt_name = '0.txt'

extract_and_save_code(txt_file_dict_path, txt_name)