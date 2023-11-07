# choose your champion
#model_id = "TheBloke/Llama-2-7B-GGML"
model_id = "TheBloke/Llama-2-7B-chat-GGML"
#model_id = "TheBloke/Llama-2-13B-GGML"
#model_id = "TheBloke/Llama-2-13B-chat-GGML"

from ctransformers import AutoModelForCausalLM

config = {'max_new_tokens': 256, 'repetition_penalty': 1.1, 'temperature': 0.1, 'stream': True}

generate_text = AutoModelForCausalLM.from_pretrained(model_id,
                                           model_type="llama",
                                           model_file="llama-2-7b-chat.ggmlv3.q5_K_M.bin",
                                           lib='avx2', #for cpu use, comment if error
                                           #gpu_layers=130, #110 for 7b, 130 for 13b
                                           **config
                                           )

print("LLM: ready")

#import time
#start_time = time.time()
## 'pipeline' execution                                                                                                             
#for word in generate_text("What is machine learning?", stream=True):
#    print(word, end='', flush=True)
#print("--- %s seconds ---" % (time.time() - start_time))
