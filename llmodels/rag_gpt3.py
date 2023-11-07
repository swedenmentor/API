from langchain.llms import OpenAI, HuggingFacePipeline
import os
import json
from dotenv import load_dotenv
load_dotenv()
os.environ["TOKENIZERS_PARALLELISM"] = "false"

#%% 1. Initializing the LLM Model (GPT-3)
#######################
# Step 1: LLM model      
#######################
llm = OpenAI(temperature=0, model_name='text-davinci-003',request_timeout=120)
print("LLM: ready")

#%% 2. Building the Knowledge Base
#######################
# Step 2: Vector DB containing the specialized data     
#######################

import pinecone
pinecone.init(  
    api_key=os.environ.get('PINECONE_API_KEY'),
    environment=os.environ.get('PINECONE_ENV')
)
index_name = 'duhocsinh-se'  
index = pinecone.Index(index_name)
print("Pinecone DB: ready")

#%% 3. Initializing the Embedding Pipeline (Hugging Face Sentence Transformer)
#######################
# Embed model                                               
# maps sentences & paragraphs to a 384-dimensional dense vector space
# and can be used for tasks like clustering or semantic search.
#######################

from langchain.embeddings.huggingface import HuggingFaceEmbeddings
embed_model_id = 'sentence-transformers/all-MiniLM-L6-v2'
device = 'cpu'
embed_model = HuggingFaceEmbeddings(
    model_name=embed_model_id,
    model_kwargs={'device': device},
    encode_kwargs={'device': device, 'batch_size': 32}
)
print("Embed model: ready")

#%% 4. Initializing the RetrievalQA Component

#######################
# Step 3: Langchain to glue them together  
#######################

from langchain.vectorstores import Pinecone
from langchain.chains import ConversationalRetrievalChain

text_field = 'text'  # field in metadata that contains text content                              
vectorstore = Pinecone(index,
                       embed_model,
                       text_field)

from langchain.memory import ConversationBufferMemory
memory = ConversationBufferMemory(
        memory_key='chat_history', return_messages=True, output_key='answer')

generate_text = ConversationalRetrievalChain.from_llm(llm=llm,
                                                      retriever=vectorstore.as_retriever(),
                                                      # get_chat_history=lambda h : h
                                                      return_source_documents=True)
print("generate_text(): ready")

#######################
# Result
#######################
#res = generate_text("What is deep convolutional nets?")
#print(res)
##
#{
#    'query': 'What is deep convolutional nets?',
#    'result': " I don't know.",
#    'source_documents': [
#        Document(
#            page_content='abc',
#            meta_data='{"source":"...url...","title":"abc"}'
#        )
#    ]
#}

def text_transform(res):
    source_documents = []
    for document in res['source_documents']:
        doc = document.to_json()
        if 'kwargs' in doc:
            source_documents.append(doc['kwargs']['metadata'])
    return json.dumps({
        'result': res['answer'],
        'source_documents': source_documents
    })

def build_prompt(messages):
    chat_history = []
    num_messages = len(messages)
    if num_messages % 2 == 1:
        num_char_in_chat_history = 0
        for i in reversed(range((num_messages-1)//2)):
            formatted_question = messages[2*i]['content']
            formatted_response = messages[2*i+1]['content'].split("\n\n&nbsp; \n\n**", 1)[0]
            if num_char_in_chat_history + len(formatted_question) + len(formatted_response) > 3841:
                break
            chat_history.insert(0, (formatted_question, formatted_response))
            num_char_in_chat_history += len(formatted_question) + len(formatted_response)
    return {"question": messages[-1]['content'], "chat_history": chat_history}
