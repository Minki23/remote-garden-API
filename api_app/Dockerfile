FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

COPY ./api_app/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY ./api_app .
COPY ./common_db ./common_db

RUN chmod +x ./prod.sh ./dev.sh

EXPOSE 3000

CMD ["sh", "./dev.sh"]
