FROM python:3.11

WORKDIR /srv

COPY . /srv/

RUN apt-get -y update

RUN cd /srv && \
    python3 setup.py bdist_wheel && \
    pip3 install dist/*.whl && \
    rm -rf /srv/*

CMD [ "python3", "-m", "homeautomation" ]
