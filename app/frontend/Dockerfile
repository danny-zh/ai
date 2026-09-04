FROM nginx:1.27-alpine

COPY index.html /usr/share/nginx/html/index.html
COPY styles.css /usr/share/nginx/html/styles.css
COPY services /usr/share/nginx/html/services
COPY src /usr/share/nginx/html/src
COPY utils /usr/share/nginx/html/utils

EXPOSE 80