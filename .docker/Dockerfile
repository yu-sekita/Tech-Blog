FROM python:3.8.0

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

ENV APP_HOME=/server
RUN mkdir $APP_HOME
RUN mkdir $APP_HOME/staticfiles

WORKDIR $APP_HOME
COPY Pipfile Pipfile.lock /server/
RUN pip install pipenv
RUN pipenv install --system
COPY ./ $APP_HOME
