#--------- Generic stuff all our Dockerfiles should start with so we get caching ------------
# Note this base image is based on debian
FROM inasafe/qgis-desktop:2.4
MAINTAINER Rizky Maulana Nugraha<lana.pcfre@gmail.com>

RUN export DEBIAN_FRONTEND=noninteractive
ENV DEBIAN_FRONTEND noninteractive
RUN dpkg-divert --local --rename --add /sbin/initctl

# Use local cached debs from host (saves your bandwidth!)
# Change ip below to that of your apt-cacher-ng host
# Or comment this line out if you do not wish to use caching
ADD 71-apt-cacher-ng /etc/apt/apt.conf.d/71-apt-cacher-ng

RUN echo "deb http://archive.ubuntu.com/ubuntu trusty main universe" > /etc/apt/sources.list
RUN apt-get -y update
RUN apt-get -y install rpl pwgen git inotify-tools

#-------------Application Specific Stuff ----------------------------------------------------
# Install QGIS 2.4, git, xvfb
RUN apt-get -y install git xvfb python-pip

ADD run-script.sh /run-script.sh
RUN chmod +x /run-script.sh
ADD helper_script/* /helper_script/

WORKDIR /home/inasafe/src/inasafe/
