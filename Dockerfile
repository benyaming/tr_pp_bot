FROM python:3.11-slim

RUN pip install pdm
WORKDIR /home/app
COPY . .
WORKDIR /home/app/tr_pp_bot
RUN pdm install
ENV PYTHONPATH=/home/app
ENV DOCKER_MODE=true
EXPOSE 8000
CMD ["pdm", "run", "python", "main.py"]
