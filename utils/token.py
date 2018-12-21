# -*- coding: utf-8 -*-
"""
    token
"""
import jwt


class CToken:
    def __init__(self):
        self.m_token_key = 'zzcontinent@163.com'
        self.m_token_algorithm = 'HS256'


token = CToken()


def encode(payload: dict, key=None, algorithm=None) -> str:
    if not key:
        key = token.m_token_key
    if not algorithm:
        algorithm = token.m_token_algorithm

    return jwt.encode(payload, key, algorithm).decode('utf8')


def decode(encoded, key=None, algorithm=None) -> dict:
    if not key:
        key = token.m_token_key
    if not algorithm:
        algorithm = token.m_token_algorithm

    return jwt.decode(encoded, key, algorithm)
