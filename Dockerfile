FROM python:3
ARG VERSION

WORKDIR /code
RUN git clone https://github.com/Shillaker/hoststats.git

WORKDIR /code/hoststats
RUN git checkout v$VERSION

RUN pip3 install -r requirements.txt
RUN pip3 install .

CMD ["hoststats", "start"]
