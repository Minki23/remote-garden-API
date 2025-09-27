FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY ./csr_signer_app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./csr_signer_app/main.py ./main.py

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
