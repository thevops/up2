FROM nginx:alpine

RUN apk add --no-cache \
        uwsgi-python3 \
        python3

RUN mkdir /domains/
RUN mkdir /app/

COPY subdomains.conf /etc/nginx/conf.d/
COPY ./server ./app

WORKDIR /app

RUN pip3 install --no-cache-dir -r requirements.txt


CMD [ "uwsgi", "--socket", "/var/run/flask.sock", \
               "--uid", "uwsgi", \
               "--plugins", "python3", \
               "--protocol", "uwsgi", \
               "--wsgi", "app:app" ]
