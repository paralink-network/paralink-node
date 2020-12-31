FROM python:3.8

RUN pip install -U pipenv

RUN adduser --disabled-password worker
USER worker
RUN mkdir /home/worker/paralink-node
RUN mkdir /home/worker/paralink-node/data
WORKDIR /home/worker/paralink-node

COPY . /node

WORKDIR /node
RUN pipenv install

EXPOSE 7424

CMD ["./paralink-node"]
