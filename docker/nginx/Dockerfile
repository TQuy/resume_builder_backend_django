FROM nginx:stable-alpine
# COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY ./static/ /static/
CMD ["nginx", "-g", "daemon off;"]