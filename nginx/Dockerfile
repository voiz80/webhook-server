FROM nginx:1.23-alpine

LABEL MAINTAINER="Ivo Dimitrov <voiz80@gmail.com>"

RUN apk --update --upgrade add --no-cache && \
apk add tzdata \
&& rm -rf /var/lib/apt/lists/*

COPY conf.d/default.conf /etc/nginx/conf.d/default.conf

ENV TZ=Europe/Sofia

EXPOSE 80 443
CMD ["nginx", "-g", "daemon off;"]