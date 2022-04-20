FROM python:3.8
VOLUME /flask/data
WORKDIR /flask/src
COPY src .
RUN pip install flask flask-cors
EXPOSE 29000
CMD python /flask/src/main.py