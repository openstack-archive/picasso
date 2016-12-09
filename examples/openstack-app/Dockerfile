FROM python:3.5

ENV PYTHONUNBUFFERED 1

RUN mkdir /code
WORKDIR /code
ADD . /code/


RUN pip3 install -r /code/requirements.txt

ENTRYPOINT ["python3", "/code/list_servers.py"]
