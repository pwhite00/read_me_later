FROM ubuntu:latest
MAINTAINER pwhite00@aol.com

ENV  PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/app
RUN apt-get update; apt-get upgrade -y; apt install python3 python3-pip -y ; pip3 install requests
RUN mkdir app/
COPY read_me_later.py app/