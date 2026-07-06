FROM debian:stable-slim
COPY edge-httpd /usr/local/bin/edge-httpd
ENV HTTP_PORT=8080 UDP_PORT=5555
EXPOSE 8080 5555/udp
CMD ["edge-httpd"]
