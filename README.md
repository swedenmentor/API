Demo: [swedenmentor.github.io](https://swedenmentor.github.io)

Frontend repo: [Link](https://github.com/swedenmentor/swedenmentor.github.io)

# Roadmap
- Pinecone-GPT3: ChatGPT API for LLM, Pinecone for Vector DB
- Weaviate-Llamma2: self-hosted Llama 2 for LLM, self-hosted Weaviate for Vector DB

![roadmap.png](archive/roadmap.png)

# Testing on local machines

## Set up environments

```bash
conda create --name rag python=3.10 -y
conda activate rag
sudo apt-get install python3-pip
pip install -r requirements.txt
```

Rename `.env.example` to `.env` and provide the corresponding API keys.

## Create database

```bash
sh build_knowledge.sh
```

## Run server API

```bash
sh serve.sh
```
The server runs at `localhost:8000`. From browser, go to `localhost:8000/q`, you should see `It is working`.

# Production deployment

Replace the following occurences of `_SITE_` with the intended domain.

## DNS

Point `api._SITE_` to server IP. Open port 8000 for TCP requests.

## Install SSL certificate for `api._SITE_`

```bash
sudo apt install nginx
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d api._SITE_
sudo certbot renew --dry-run
cp /etc/letsencrypt/live/api._SITE_/fullchain.pem cert.pem
cp /etc/letsencrypt/live/api._SITE_/privkey.pem key.pem
```

The frontend server should also have SSL certificate.

## Set up environments

```bash
sudo apt install software-properties-common -y
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install python3.10
sudo apt install python3-pip
pip install -r requirements.txt
```

## Create database

```bash
sh build_knowledge.sh
```

## Run server API
```bash
sh serve.sh
```
