FROM homeassistant/home-assistant:stable

RUN python3 -m pip install "green-energy==0.1.0"

COPY configuration.yaml /config/configuration.yaml
