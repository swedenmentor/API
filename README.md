# Testing on local machines

## Set up environments

```
conda create --name rag python=3.10 -y
conda activate rag
sudo apt-get install python3-pip
pip install -r requirements.txt
```

## LLM model

```
python llm.py
```

## Vector DB with specialized data

```
python pinecone_index.py
python pinecone_test.py
```

## RAG implementation (TODO)

```
python rag.py
```

## Run server API

```
python api.py
```
The server runs at localhost:8000

# Server deloyment

## DNS

Point api.__SITE__ to server IP

## Install SSL certificate for api.__SITE__

```
sudo apt get nginx
sudo git clone https://github.com/certbot/certbot /opt/letsencrypt
sudo certbot --nginx -d api._SITE
sudo certbot renew --dry-run
```

## Deploy using Nginx and Gunicorn (TODO)
