FROM python:3.12-slim

WORKDIR /app

COPY app/backend/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

COPY app /app/app

EXPOSE 8001

CMD ["uvicorn", "app.backend.src.app:app", "--host", "0.0.0.0", "--port", "8001"]