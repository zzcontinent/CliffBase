# -*- coding: utf-8 -*-
"""
    token
"""
import jwt
from utils.config import config


def encode(payload: dict, key=None, algorithm=None) -> str:
    if not key:
        key = config.token_key
    if not algorithm:
        algorithm = config.token_algorithm

    return jwt.encode(payload, key, algorithm).decode('utf8')


def decode(encoded, key=None, algorithm=None) -> dict:
    if not key:
        key = config.token_key
    if not algorithm:
        algorithm = config.token_algorithm

    return jwt.decode(encoded, key, algorithm)
