FROM python:3

WORKDIR /code
RUN pip3 install -r /tmp/requirements.txt
RUN pip3 install -e .

CMD ["hoststats", "start"]

