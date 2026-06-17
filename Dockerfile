FROM python:3.11-slim

WORKDIR /app


COPY system-monitor-api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY system-monitor-api/ .

EXPOSE 5000

CMD ["python", "app.py"]