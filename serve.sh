SSL_KEY_FILE=key.pem
SSL_CERT_FILE=cert.pem

if [ -f "$SSL_CERT_FILE" ]; then
    #gunicorn --keyfile key.pem --certfile cert.pem --config gunicorn_config.py api:app
    hypercorn --keyfile $SSL_KEY_FILE --certfile $SSL_CERT_FILE --bind 0.0.0.0:8000 --workers 2 stream_api:app
else
    #flask --app api run -h 0.0.0.0 -p 8000
    hypercorn --bind 0.0.0.0:8000 --reload stream_api:app
fi
