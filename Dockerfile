FROM python:3

WORKDIR /code

COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

RUN pip3 install -e .

CMD ["hoststats", "start"]

