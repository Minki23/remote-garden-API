FROM python:3.11-slim

WORKDIR /app

RUN pip install uv

COPY pyproject.toml uv.lock ./
RUN uv pip install --system .

COPY app ./app
COPY prod.sh ./prod.sh
COPY dev.sh ./dev.sh

RUN chmod +x ./prod.sh ./dev.sh

EXPOSE 3000

CMD ["sh", "./dev.sh"]
