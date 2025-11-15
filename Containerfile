FROM python:3.13-alpine

LABEL name="APOrganizer"
LABEL description="Archipelago organizer bot for Discord."

WORKDIR /app
COPY . .
RUN pip install .

ENTRYPOINT ["aporganizer"]
