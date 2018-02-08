#--------- Generic stuff all our Dockerfiles should start with so we get caching ------------
FROM debian:jessie

RUN apt-get -y update; apt-get -y --force-yes install apt-transport-https
RUN apt-key adv --keyserver keyserver.ubuntu.com --recv-key 3FF5FFCAD71472C4

RUN echo "deb     http://qgis.org/debian jessie main" >> /etc/apt/sources.list
RUN echo "deb-src http://qgis.org/debian jessie main" >> /etc/apt/sources.list

RUN apt-get -y update; apt-get -y --force-yes install qgis python-qgis
RUN apt-get -y update; apt-get -y --force-yes install build-essential autoconf libtool pkg-config

RUN export DEBIAN_FRONTEND=noninteractive
ENV DEBIAN_FRONTEND noninteractive
RUN dpkg-divert --local --rename --add /sbin/initctl

RUN apt-get -y update; apt-get -y --force-yes install pwgen git inotify-tools

#-------------Application Specific Stuff ----------------------------------------------------
# Install git, xvfb
RUN apt-get -y update; apt-get -y --force-yes install git xvfb python-setuptools python-dev libssl-dev libffi-dev python-scipy
RUN easy_install pip==9.0.1
# Copy ubuntu fonts
RUN apt-get -y update; apt-get -y --force-yes install wget unzip
ADD ubuntu-font-family-0.83.zip /ubuntu-font-family-0.83.zip
RUN unzip ubuntu-font-family-0.83.zip
RUN mv ubuntu-font-family-0.83 /usr/share/fonts/truetype/ubuntu-font-family
RUN fc-cache -f -v

ADD REQUIREMENTS.txt /REQUIREMENTS.txt
RUN pip install -r REQUIREMENTS.txt

ADD docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

# Install InaSAFE Core
RUN mkdir -p /usr/share/qgis/python/plugins
WORKDIR /usr/share/qgis/python/plugins
ARG INASAFE_CORE_TAG=develop
RUN git clone --branch ${INASAFE_CORE_TAG} --depth 1 --recursive https://github.com/inasafe/inasafe.git inasafe

# Install InaSAFE Headless
RUN mkdir -p /home/app
WORKDIR /home/app
ARG INASAFE_HEADLESS_TAG=develop
RUN git clone --branch ${INASAFE_HEADLESS_TAG} --depth 1 https://github.com/inasafe/inasafe-headless.git source
RUN ln -s source/src/headless headless

CMD ["/docker-entrypoint.sh"]
