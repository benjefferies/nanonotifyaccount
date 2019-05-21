FROM python:3.6.8-slim-jessie

EXPOSE 5000

WORKDIR /app
COPY . /app
RUN pip3 install pipenv==8.3.1 && pipenv install --deploy --system

CMD ["gunicorn", "-w", "7", "-b", "0.0.0.0:5000", "run:app"]
