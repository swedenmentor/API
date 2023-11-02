Demo: [chat.duhocsinh.se](https://chat.duhocsinh.se)

Frontend repo: [tuananhdao/chat.duhocsinh.ui](https://github.com/tuananhdao/chat.duhocsinh.ui)

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
python api.py
```
The server runs at localhost:8000

# Production deloyment

## DNS

Point api.__SITE__ to server IP

## Install SSL certificate for api.__SITE__

```bash
sudo apt get nginx
sudo git clone https://github.com/certbot/certbot /opt/letsencrypt
sudo certbot --nginx -d api._SITE
sudo certbot renew --dry-run
```

## Deploy using Nginx and Gunicorn (TODO)
