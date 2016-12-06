FROM python:3.5

ENV PYTHONUNBUFFERED 1

RUN mkdir /code
WORKDIR /code
ADD . /code/


RUN pip3 install -r /code/requirements.txt
RUN python3 /code/setup.py install


ENTRYPOINT ["python3", "/code/service/picasso_api.py"]
EXPOSE 10001
