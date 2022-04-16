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

# install git
RUN apt install git

# create dcss folders
RUN mkdir dcss
RUN cd dcss/
RUN git clone https://github.com/crawl/crawl.git
RUN cd crawl/
RUN git reset –-hard 6321bf748524f7d0293791ef762c9fc6f8cecf2e

# Expose Port for the Application
EXPOSE 8080