#Junos Statsd monitoring


This tool is to retrieve custom data from Juniper Operation System and send it
to Statsd server. To run this  a config file is needed with the following data:

```
statsd:
  host: "127.0.0.1"
  port: 8125
  prefix: ""
junos:
  <label>:
    user: '<username>'
    password: '<password>'
    host: '<host>'
    port: '<port>'
    commands:
      - "show security monitoring node all"
      - "show system buffers"
      - "show route summary"
```


The following command need to be run each time that we want to send data:

```
docker run --rm -v "$(pwd):/opt/junos_statsd/" eloycoto/junos_statsd
```
