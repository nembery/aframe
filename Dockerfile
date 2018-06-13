FROM python:2.7

LABEL description="AFrame - Minimal API UI Framework"
LABEL version="1.1"
LABEL maintainer="nembery@gmail.com"

WORKDIR /app
ADD requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt

COPY . /app/aframe/
RUN  python /app/aframe/manage.py migrate

EXPOSE 8000

ENTRYPOINT ["python"]
CMD ["/app/aframe/manage.py", "runserver", "0.0.0.0:8000"]
