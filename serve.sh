SSL_KEY_FILE=key.pem
SSL_CERT_FILE=cert.pem

if [ -f "$SSL_CERT_FILE" ]; then
    gunicorn --keyfile key.pem --certfile cert.pem --config gunicorn_config.py api:app
else
    flask --app api run -h 0.0.0.0 -p 8000
fi
