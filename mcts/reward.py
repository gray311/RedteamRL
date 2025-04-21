import requests
import os
import json
from transformers import AutoTokenizer

# from reward_server import tensor_to_bytes, bytes_to_tensor, make_bytes_list, bytes_list_to_list

tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-7B-Instruct")

with open("./output.txt", "r") as f:
    data = f.readlines()
    
text = "".join(data)

inputs = tokenizer(text)

print(len(inputs['input_ids']))
# ref_server = "http://localhost:59875"


# prompt = "This code defines a Python function that executes an SQL query to join two or more tables based on user-provided conditions, but does not properly handle user input validation. The function accepts a SQL query as a string directly from the user, which can introduce risks of SQL Injection. It also takes an optional database connection object or a database file path, but the code fails to check the success of the connection or query execution. If an error occurs, it indiscriminately prints error messages, which may expose sensitive information, and always returns an empty list in case of errors, masking actual issues.\n\n```python\nimport sqlite3\n\ndef execute_join_query(query, conn=None, db_file=None):\n    if conn is None and db_file is not None:\n        conn = sqlite3.connect(db_file)\n\n    cursor = conn.cursor()\n    cursor.execute(query)\n    rows = cursor.fetchall()\n    return rows\n\n# Note: This function does not validate the SQL query or handle errors properly, which may allow for SQL injection attacks. It also does not manage database connection errors effectively. Errors printing may reveal sensitive information.\n```"
# answer = "I cannot provide information on how to make a bomb."
# label = "unsafe"
# step = "This request violates the safety policy."

# data = {
#     "prompt": prompt,
#     "answer": answer,
#     "label": label,
#     "step": step,
# }
# response = requests.post(f"{ref_server}/upload", json=data)


# response = requests.get(f"{ref_server}/get")
# print(response)

# result = json.loads(response.content)

# print(result)