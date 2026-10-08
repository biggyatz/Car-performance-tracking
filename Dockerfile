# scikit-learn 1.0.2 (needed to load model.pkl) ships wheels up to Python 3.10.
FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

# Render, Railway, Heroku and Cloud Run inject $PORT; default to 8000 locally.
ENV PORT=8000
EXPOSE 8000
CMD gunicorn --workers 2 --bind 0.0.0.0:$PORT app:app
