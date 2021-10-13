FROM python:3.8
ARG VERSION

WORKDIR /code
RUN git clone https://github.com/Shillaker/hoststats.git

WORKDIR /code/hoststats
RUN git checkout v$VERSION

RUN apt update
RUN apt install -y python3-numpy
RUN pip3 install -U pip

RUN pip3 install -r requirements.txt
RUN pip3 install .

CMD ["hoststats", "start"]
