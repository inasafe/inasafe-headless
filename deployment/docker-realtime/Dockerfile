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

# This section taken on 2 July 2015 from
# https://docs.docker.com/examples/running_ssh_service/
# Sudo is needed by pycharm when it tries to pip install packages
RUN apt-get update -y; apt-get install -y --force-yes openssh-server sudo
RUN mkdir /var/run/sshd
RUN echo 'root:docker' | chpasswd
RUN sed -i 's/PermitRootLogin without-password/PermitRootLogin yes/' /etc/ssh/sshd_config

# SSH login fix. Otherwise user is kicked off after login
RUN sed 's@session\s*required\s*pam_loginuid.so@session optional pam_loginuid.so@g' -i /etc/pam.d/sshd

ENV NOTVISIBLE "in users profile"
RUN echo "export VISIBLE=now" >> /etc/profile

# End of cut & paste section

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

ADD run-env-linux.sh /run-env-linux.sh
ADD docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

# Environment variable
ENV C_FORCE_ROOT="True" \
	PYTHONPATH="/home/app" \
	DISPLAY=":99" \
	INASAFE_HEADLESS_BROKER_HOST="amqp://guest:guest@rabbitmq:5672/" \
	QGIS_LOG_FILE="/tmp/inasafe/headless/logs/qgis.log" \
	QGIS_DEBUG_FILE="/tmp/inasafe/headless/logs/qgis-debug.log" \
	QGIS_DEBUG="0" \
	INASAFE_WORK_DIR="/tmp/inasafe"

CMD ["./docker-entrypoint.sh", "prod", "inasafe-headless"]
