#--------- Generic stuff all our Dockerfiles should start with so we get caching ------------
FROM kartoza/qgis-desktop:2.18

RUN apt-get -y update; apt-get -y --force-yes install pwgen git inotify-tools

# This section taken on 2 July 2015 from
# https://docs.docker.com/examples/running_ssh_service/
# Sudo is needed by pycharm when it tries to pip install packages
RUN apt-get update -y; apt-get install -y --force-yes openssh-server sudo
RUN mkdir /var/run/sshd
RUN echo 'root:docker' | chpasswd
RUN sed -i 's/PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config

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

ADD sitecustomize.py /usr/local/lib/python2.7/site-packages/sitecustomize.py
ADD REQUIREMENTS.txt /REQUIREMENTS.txt
RUN pip install -r REQUIREMENTS.txt

ADD docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

# Environment variable
ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["prod", "inasafe-headless-worker"]
