FROM python:3.9

WORKDIR /foodgram

COPY . /foodgram/

RUN pip install --upgrade pip

RUN pip install -r requirements.txt

RUN pip install gunicorn==20.1.0

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "foodgram.wsgi"]
