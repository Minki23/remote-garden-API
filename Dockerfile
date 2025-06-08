FROM python:3.11-slim

WORKDIR /app

# System dependencies for OpenCV
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgl1 \
 && rm -rf /var/lib/apt/lists/*

RUN pip install uv

COPY pyproject.toml uv.lock ./
RUN uv pip install --system .

COPY app ./app
COPY prod.sh ./prod.sh
COPY dev.sh ./dev.sh

RUN chmod +x ./prod.sh ./dev.sh

EXPOSE 3000

CMD ["sh", "./dev.sh"]
