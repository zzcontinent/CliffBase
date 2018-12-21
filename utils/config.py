# -*- coding: utf-8 -*-
import platform
import yaml


def get_system_platform():
    return platform.system()


def get_config_path():
    if get_system_platform() == 'Windows':
        return r'C:\etc\DBConfig.yaml'
    else:
        return r'/etc/metadata/DBConfig.yaml'


def read_yaml(file_path):
    with open(file_path) as in_file:
        return yaml.load(in_file)


yaml_dict = read_yaml(get_config_path())

