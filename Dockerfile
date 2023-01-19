FROM homeassistant/home-assistant:stable

RUN python3 -m pip install "green_energy_api==0.1.0"

COPY configuration.yaml /config/configuration.yaml
