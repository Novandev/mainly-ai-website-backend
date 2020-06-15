source venv/bin/activate
pip install -r requirements.txt
wait
gunicorn --bind 0.0.0.0:5000 wsgi:app