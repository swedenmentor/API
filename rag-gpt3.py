from langchain.llms import OpenAI, HuggingFacePipeline
from dotenv import load_dotenv  
import os

load_dotenv()

#######################
# Step 1: LLM model      
#######################
llm = OpenAI(temperature=0, model_name='text-davinci-003')

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

# embed model?? TA: I do not understand this part                                                
from langchain.embeddings.huggingface import HuggingFaceEmbeddings
embed_model_id = 'sentence-transformers/all-MiniLM-L6-v2'
device = 'cpu'
embed_model = HuggingFaceEmbeddings(
    model_name=embed_model_id,
    model_kwargs={'device': device},
    encode_kwargs={'device': device, 'batch_size': 32}
)

#######################
# Step 3: Langchain to glue them together  
#######################

from langchain.vectorstores import Pinecone
from langchain.chains import RetrievalQA

text_field = 'text'  # field in metadata that contains text content                              
vectorstore = Pinecone(index,
                       embed_model.embed_query,
                       text_field)  
generate_text = RetrievalQA.from_chain_type(llm=llm,
                                           chain_type='stuff',
retriever=vectorstore.as_retriever())
