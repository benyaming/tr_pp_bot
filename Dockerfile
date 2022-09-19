FROM python:3.10-slim

RUN pip install pipenv
WORKDIR /home/app
COPY . .
WORKDIR /home/app/bot
RUN poetry update
ENV PYTHONPATH=/home/app
ENV DOCKER_MODE=true
EXPOSE 8000
CMD ["poetry", "run", "python", "main.py"]
