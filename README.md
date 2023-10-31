# Testing on local machines

## Set up environments

```conda create rag
conda activate rag
conda install python=3.10
pip install -r requirements.txt
```

## LLM model

```python llm.py
```

## Vector DB with specialized data

```python pinecone_index.py
python pinecone_test.py
```

## RAG implementation (TODO)

## Run server API

```python api.py
```

# Server deloyment

## DNS

Point api._SITE_ to server IP

## Install SSL certificate for api._SITE_

```sudo apt get nginx
sudo git clone https://github.com/certbot/certbot /opt/letsencrypt
sudo certbot --nginx -d api._SITE
sudo certbot renew --dry-run
```

## Deploy using Nginx and Gunicorn (TODO)