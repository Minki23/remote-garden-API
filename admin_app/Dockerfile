FROM python:3.11-slim

WORKDIR /admin_app

RUN apt-get update && apt-get install -y \
    libpq-dev

COPY ./admin_app/ ./
COPY ./app /admin_app/app

RUN pip install \
    fastapi \
    uvicorn \
    sqladmin \
    sqlalchemy \
    asyncpg \
    jinja2 \
    psycopg2-binary

EXPOSE 8001

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
