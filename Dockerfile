FROM python:3.9.2-slim

WORKDIR /srv/media-api/
EXPOSE 8000

ENV FILE_STORAGE tmp
ENV UPLOADED_FILES_DIR uploaded
ENV TRANSFORMED_FILES_DIR transformed

RUN apt-get update && apt-get install -y make && rm -rf /var/lib/apt/lists/*

COPY ./Makefile ./Makefile
COPY ./requirements.txt ./requirements.txt
COPY . .

RUN make prod-init

CMD ["uvicorn", "--host", "0.0.0.0", "--workers", "4", "--loop", "uvloop", "main:app"]
