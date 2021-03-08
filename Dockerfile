FROM python:3.8

RUN wget https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh -O /wait-for-it.sh && chmod +x /wait-for-it.sh

RUN pip install -U pipenv

RUN mkdir /home/worker/paralink-node
RUN mkdir /home/worker/paralink-node/data
WORKDIR /home/worker/paralink-node

COPY . /node

WORKDIR /node
RUN pipenv install

EXPOSE 7424

CMD ["./paralink-node"]
