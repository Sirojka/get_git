FROM python:3.7-slim

RUN ["apt-get", "update"]
RUN ["apt-get", "upgrade", "-y"]
RUN ["apt-get", "install", "-y", "tzdata"]
RUN ["ln", "-fs", "/usr/share/zoneinfo/Europe/Minsk", "/etc/localtime"]
RUN ["dpkg-reconfigure","-f", "noninteractive", "tzdata"]
ENV TZ="Europe/Minsk"

COPY requirements.txt /opt/
RUN mkdir /opt/get_git
RUN ["pip", "install", "-r", "/opt/requirements.txt"]
RUN rm /opt/requirements.txt
# copy src code to image
COPY . /opt/get_git/
WORKDIR /opt/get_git/
