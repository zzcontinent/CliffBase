# -*- coding: utf-8 -*-
"""
    token
"""
import jwt


class CToken:
    def __init__(self):
        self.m_token_key = 'zzcontinent@163.com'
        self.m_token_algorithm = 'HS256'
        self.m_expire = 60 * 60 * 12
        self.m_token = ''

    def enc(self, payload):
        return jwt.encode(payload=payload, key=self.m_token_key, algorithm=self.m_token_algorithm)

    def dec(self, token=None):
        if not token:
            token = self.m_token
        return jwt.decode(jwt=token, key=self.m_token_key, algorithms=self.m_token_algorithm)


token = CToken()


def main():
    token.m_token = token.enc('123')
    print(token.m_token)
    print(token.dec())


if __name__ == '__main__':
    main()
