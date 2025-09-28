FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir paho-mqtt==1.6.1

COPY ./mock_mqtt_app .

ENV DEVICE_MAC="00:00:00:00:00:00"
ENV USER_KEY="default_user_key"

CMD ["python", "/app/mock_device_publisher.py"]
