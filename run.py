#!/usr/bin/env python

import argparse
import statsd
import threading
import yaml
from jnpr.junos import Device


def ToDOT(root, prefix):
    prefix += ".{0}".format(root.tag.title().replace("-", ""))
    if len(root.getchildren()) == 0:
        result = root.attrib.get("name", root.text)
        if result.isdigit():
            yield(prefix, result)
    for elem in root.getchildren():
        for e in ToDOT(elem, prefix):
            yield e


class Junos(threading.Thread):

    def __init__(self, label, host, user, password, port=22, commands=[]):
        threading.Thread.__init__(self)
        self.label = label.replace("-", "")
        self.dev = Device(
            user=user,
            password=password,
            host=host,
            port=port)
        self.commands = commands
        self.result = []

    def gather_data(self):
        for command in self.commands:
            root = self.dev.cli(command, format="xml")
            for e in ToDOT(root, self.label):
                self.result.append(e)

    def run(self):
        self.dev.open()
        result = self.gather_data()
        self.dev.close()
        return result


def run():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", help="config file")
    args = parser.parse_args()
    if not args.config:
        args.config = "/opt/junos_statsd/data.yml"

    with open(args.config, "r") as fp:
        config = yaml.load(fp)
    threads = []
    for k, v in config.get("junos").items():
        junos = Junos(k, **v)
        junos.start()
        threads.append(junos)

    client = statsd.StatsClient(
        config.get('statsd', {}).get("host", "127.0.0.1"),
        config.get('statsd', {}).get("port", 8125))
    prefix = "{}"
    if config.get('statsd', {}).get("prefix"):
        prefix = "{0}.{1}".format(
            config.get('statsd', {}).get("prefix"))

    [x.join() for x in threads]

    for x in threads:
        for k, v in x.result:
            client.gauge(prefix.format(k), v)

if __name__ == "__main__":
    run()
