# -*- coding: gbk -*-

import hashlib

def encode_md5(s):
    m = hashlib.md5(s)
    return m.hexdigest()[8 : -8]
