FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY app ./app
COPY prod.sh ./prod.sh
COPY dev.sh ./dev.sh

RUN chmod +x ./prod.sh ./dev.sh

EXPOSE 3000

CMD ["sh", "./dev.sh"]
