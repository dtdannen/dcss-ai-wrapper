#Download base image ubuntu 20.04
FROM ubuntu:20.04

# LABEL about the custom image
LABEL maintainer="dustin.dannenhauer@outlook.com"
LABEL version="0.1"
LABEL description="This is custom Docker Image running Dungeon Crawl Stone Soup in webserver mode with premade logins."

# Disable Prompt During Packages Installation
ARG DEBIAN_FRONTEND=noninteractive

# Update Ubuntu Software repository
RUN apt update

# get all tools to compile crawl
RUN apt -y install build-essential libncursesw5-dev bison flex liblua5.1-0-dev libsqlite3-dev
RUN apt -y install libz-dev pkg-config python3-yaml binutils-gold python-is-python3 python2 make
RUN apt -y install libsdl2-image-dev libsdl2-mixer-dev libsdl2-dev libfreetype6-dev libpng-dev
RUN apt -y install fonts-dejavu-core advancecomp pngcrush git python3.8-venv

# create dcss folder at root level
RUN mkdir dcss

### clone from git and reset to 26.1 version
WORKDIR /dcss/
RUN git clone --recurse-submodules -j8 https://github.com/crawl/crawl.git crawl/
WORKDIR /dcss/crawl/
RUN git reset --hard "d7a4d63c155831395aa76a5b27c080510dfb948e"

# copying sprint files from ai-wrapper to dcss folder
COPY ../custom_sprints/* /dcss/crawl/crawl-ref/source/dat/des/sprint

# compile crawl
WORKDIR /dcss/crawl/crawl-ref/source/
RUN make install prefix=/usr/local WEBTILES=y

# RCS is a folder that is used by players, need to create it for webserver to work correctly
RUN mkdir /dcss/crawl/crawl-ref/source/rcs/

# Expose Port for the Application
EXPOSE 8080

# create a virtual env for running the webserver
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# install packages needed for webserver
RUN pip install tornado pyyaml

# Set up for running the webserver automatically
WORKDIR /dcss/crawl/crawl-ref/source

# Run the webserver
CMD ["python", "webserver/server.py" ]
