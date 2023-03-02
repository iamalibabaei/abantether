FROM python:3.9-alpine3.14

# ENVs
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install psycopg2 dependencies
RUN apk update \
    && apk add postgresql-dev gcc python3-dev musl-dev

# Working Dir
RUN mkdir /task
WORKDIR /task

# Install dependencies
RUN pip install --upgrade pip
COPY requirements/base.txt /task/requirements/
COPY requirements/production.txt /task/requirements/
RUN pip install -r requirements/production.txt

# Copy entrypoint.sh
COPY ./entrypoint.sh .
RUN sed -i 's/\r$//g' /task/entrypoint.sh
RUN chmod +x /task/entrypoint.sh

# Copy project
COPY . .

# Run entrypoint
ENTRYPOINT ["sh", "/task/entrypoint.sh"]