FROM python:3.8
VOLUME /flask/data
VOLUME /flask/src
WORKDIR /flask/src
# COPY src .
COPY ./requirements.txt /flask/requirements.txt
RUN pip install -r /flask/requirements.txt
EXPOSE 80
# CMD python /flask/src/main.py
CMD ["gunicorn", "main:app", "-c", "./gunicorn.conf.py"]