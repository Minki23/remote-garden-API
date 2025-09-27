FROM python:3.11-slim

WORKDIR /admin_app

RUN apt-get update && apt-get install -y \
    libpq-dev

COPY ./admin_app .
COPY ./common_db ./common_db

RUN pip install -r ./requirements.txt

EXPOSE 8001

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
