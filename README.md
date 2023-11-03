Demo: [chat.duhocsinh.se](https://chat.duhocsinh.se)

Frontend repo: [tuananhdao/chat.duhocsinh.ui](https://github.com/tuananhdao/chat.duhocsinh.ui)

# Roadmap
- Pinecone-GPT3: ChatGPT API for LLM, Pinecone for Vector DB
- Weaviate-Llamma2: self-hosted Llama 2 for LLM, self-hosted Weaviate for Vector DB

# Testing on local machines

## Set up environments

```bash
conda create --name rag python=3.10 -y
conda activate rag
sudo apt-get install python3-pip
pip install -r requirements.txt
```

Rename `.env.example` to `.env` and provide the corresponding API keys.

## Run server API

```bash
sh serve.sh
```
The server runs at `localhost:8000`. From browser, go to `localhost:8000/q`, you should see `It is working`.

# Production deloyment

## DNS

Point `api._SITE_` to server IP

## Install SSL certificate for `api._SITE_`

```bash
sudo apt get nginx
sudo git clone https://github.com/certbot/certbot /opt/letsencrypt
sudo certbot --nginx -d api._SITE
sudo certbot renew --dry-run
```
Copy the key file as `key.pem` and the cert file as `cert.pem` to the repo folder.

## Run server API
```bash
sh serve.sh
```