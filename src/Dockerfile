# Create the base OS image
FROM python:3.12.2 AS base

# Create Volumes
VOLUME /logs
VOLUME /config

# Install python requirements
FROM base AS requirements

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

# Install and run Hanekawa
COPY ./Hanekawa ./Hanekawa/

ENTRYPOINT ["python3", "-m", "Hanekawa"]
CMD ["config.toml"]