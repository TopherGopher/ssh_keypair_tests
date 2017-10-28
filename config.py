#!/usr/local/bin/python
import yaml


def load_from_yaml(config):
    with open('config.yml') as fp:
        config.update(yaml.load(fp))
    return config

config = load_from_yaml({})
