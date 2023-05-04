FROM python:3.9.16-alpine3.17

LABEL MAINTAINER="Ivo Dimitrov <idimitrov@easypay.bg>"

WORKDIR /app
COPY . /app

RUN apk --update --upgrade add --no-cache && \
apk add tzdata && \
python -m pip install --upgrade pip && \
pip install -r requirements.txt && \
pip install gunicorn \
&& rm -rf /var/lib/apt/lists/*

ENV TZ=Europe/Sofia

EXPOSE 5000

CMD [ "gunicorn", "-w", "4", "--bind", "0.0.0.0:5000","--log-level=debug", "wsgi:app", "--reload"]