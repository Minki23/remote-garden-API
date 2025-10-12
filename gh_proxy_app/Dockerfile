FROM python:3.11-slim

WORKDIR /app

COPY gh_proxy_app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY gh_proxy_app/ ./

EXPOSE 7999

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7999"]