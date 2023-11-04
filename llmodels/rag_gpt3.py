from langchain.llms import OpenAI, HuggingFacePipeline
from dotenv import load_dotenv
import os
import json

load_dotenv()
os.environ["TOKENIZERS_PARALLELISM"] = "false"

#%% 1. Initializing the LLM Model (GPT-3)
#######################
# Step 1: LLM model      
#######################
llm = OpenAI(temperature=0, model_name='text-davinci-003')



#%% 2. Building the Knowledge Base
#######################
# Step 2: Vector DB containing the specialized data     
#######################

import pinecone
pinecone.init(  
    api_key=os.environ.get('PINECONE_API_KEY'),
    environment=os.environ.get('PINECONE_ENV')
)
index_name = 'llama-2-rag'  
index = pinecone.Index(index_name)


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

#%% 4. Initializing the RetrievalQA Component

#######################
# Step 3: Langchain to glue them together  
#######################

from langchain.vectorstores import Pinecone
from langchain.chains import RetrievalQA

text_field = 'text'  # field in metadata that contains text content                              
vectorstore = Pinecone(index,
                       embed_model,
                       text_field)
generate_text = RetrievalQA.from_chain_type(llm=llm,
                                            chain_type='stuff',
                                            retriever=vectorstore.as_retriever(),
                                            return_source_documents=True)

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
        source_documents.append(doc['kwargs']['metadata'])
    return json.dumps({
        'result': res['result'],
        'source_documents': source_documents
    })

#print(text_transform(generate_text("What is deep convolutional nets?")))
