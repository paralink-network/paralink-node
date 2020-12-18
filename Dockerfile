FROM python:3.8

COPY . /node

WORKDIR /node
RUN pip install -U pipenv
RUN pipenv install

EXPOSE 7424

CMD ["./paralink-node"]
