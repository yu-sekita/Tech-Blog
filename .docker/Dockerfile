FROM python:3.8
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /server
COPY Pipfile Pipfile.lock /server/
RUN pip install pipenv && pipenv install --system
COPY ./ /server