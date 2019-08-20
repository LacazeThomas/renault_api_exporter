# Renault Api Exporter


#### Replace in 'config.yml' your credientials and VIN

#### Start docker container :
```
docker run -d -p 9158:9158 --name=renault_api_exporter --restart=always -v $(pwd)/config.yml/:/opt/renault_api_exporter/config.yml renault_api_exporter:latest
```

#### Prometheus is now running in 'host:9158/metrics
