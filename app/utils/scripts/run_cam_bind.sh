ffmpeg -rtsp_transport tcp \
  -i rtsp://admin:admin123@192.168.100.9:554/h264Preview_01_main \
  -f rtsp rtsp://127.0.0.1:8554/live

# mediamtx is required

# you can install it by follow:
# wget https://github.com/bluenviron/mediamtx/releases/latest/download/mediamtx_v1.12.3_linux_amd64.tar.gz
# tar -xzf mediamtx_v1.12.3_linux_amd64.tar.gz
# ./mediatmx