FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=news_analysis_service.py

EXPOSE 5055

CMD ["gunicorn", "--bind", "0.0.0.0:5055", "news_analysis_service:app"] 