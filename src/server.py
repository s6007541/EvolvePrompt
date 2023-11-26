import os
os.environ["CUDA_VISIBLE_DEVICES"] = "7"

from flask import Flask, request, jsonify
from llama import Llama
from config import *

app = Flask(__name__)

model = Llama.build(
    ckpt_dir=model_path,
    tokenizer_path=tokenizer_path,
    max_seq_len=max_seq_len,
    max_batch_size=max_batch_size,
)

@app.route('/', methods=['POST'])
def predict():
    # Get input data (you need to replace this with your actual data)
    content = request.json
    messages = content.get('messages')
    completion = model.chat_completion(
            [messages],  # type: ignore
            max_gen_len=256,
            temperature=temperature,
            top_p=top_p
    )
    # Return the predictions as JSON
    return completion

def hello():
    return 'Hello, World!'

if __name__ == '__main__':
    app.run(port=8794)
