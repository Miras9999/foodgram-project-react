FROM python:3.9

WORKDIR /foodgram

COPY . /foodgram/

RUN pip install --upgrade pip

RUN pip install -r requirements.txt

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "foodgram.wsgi"]
