FROM ubuntu:20.04

WORKDIR /usr/app/src

RUN apt-get update

RUN apt-get install -y python3-pip python3-dev \
  && cd /usr/local/bin \
  && ln -s /usr/bin/python3 python \
  && pip3 install --upgrade pip

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY . ./

CMD ["sh", "-c", "streamlit run --server.port 7000 /usr/app/src/app.py"]