from llama import Llama
import pickle

ckpt_dir = "/mnt/sting/sorn111930/cut/codellama/CodeLlama-34b-Instruct/"
tokenizer_path = "/mnt/sting/sorn111930/cut/codellama/CodeLlama-34b-Instruct/tokenizer.model"
max_seq_len = 512
max_batch_size = 4
max_gen_len = None
top_p = 0.95
temperature = 0.2

with open('temp.pkl', 'rb') as f:
    messages = pickle.load(f)
            

generator = Llama.build(
    ckpt_dir=ckpt_dir,
    tokenizer_path=tokenizer_path,
    max_seq_len=max_seq_len,
    max_batch_size=max_batch_size,
)

# with open("/mnt/sting/sorn111930/cut/ChatUniTest/src/messages.txt", 'w') as f1:
    
    
# Retry 5 times when error occurs

# messages = [
#         [
#             {
#                 "role": "user",
#                 "content": "In Bash, how do I list all text files in the current directory (excluding subdirectories) that have been modified in the last month?",
#             }
#         ],
#         [
#             {
#                 "role": "user",
#                 "content": "What is the difference between inorder and preorder traversal? Give an example in Python.",
#             }
#         ],
#         [
#             {
#                 "role": "system",
#                 "content": "Provide answers in JavaScript",
#             },
#             {
#                 "role": "user",
#                 "content": "Write a function that computes the set of sums of all contiguous sublists of a given list.",
#             }
#         ],
#     ]

max_try = 1
while max_try:
        
    completion = generator.chat_completion(
                [messages],  # type: ignore
                max_gen_len=max_gen_len,
                temperature=temperature,
                top_p=top_p
    )

    # with open(save_path, "w") as f:
    #     json.dump(completion, f) # result is here in completion
    #     print(completion)
    # # return True  
    max_try -= 1
print(completion)
    
# return False
