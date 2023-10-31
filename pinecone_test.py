import os
import pinecone
from dotenv import load_dotenv

load_dotenv()

# get API key from app.pinecone.io and environment from console
pinecone.init(
    api_key=os.environ.get('PINECONE_API_KEY') or 'PINECONE_API_KEY',
    environment=os.environ.get('PINECONE_ENV') or 'PINECONE_ENV'
)

import time

index_name = 'llama-2-rag'

if index_name not in pinecone.list_indexes():
    pinecone.create_index(
        index_name,
        dimension=len(embeddings[0]),
        metric='cosine'
    )
    # wait for index to finish initialization
    while not pinecone.describe_index(index_name).status['ready']:
        time.sleep(1)

index = pinecone.Index(index_name)
print(index.describe_index_stats())
