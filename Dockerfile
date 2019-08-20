FROM python:3.7.4-alpine

COPY renault_api_exporter/ /opt/renault_api_exporter/

RUN pip3 install -r /opt/renault_api_exporter/requirements.txt
RUN touch /opt/renault_api_exporter/config.yml
EXPOSE 9158

ENTRYPOINT ["python3", "/opt/renault_api_exporter/exporter.py", "/opt/renault_api_exporter/config.yml"]
