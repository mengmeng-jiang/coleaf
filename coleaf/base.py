#!/usr/bin/env python

import os
import os.path as op

def findByDepth(base, suffix=['jpg']):
    for root, dirs, files in os.walk(base):
        for fname in files:
            if fname.rsplit(".", 1)[-1] in suffix:
                fullname = op.join(root, fname)
                yield fullname