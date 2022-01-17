import os
import simplejson as json
import numpy as np


def ensure_dir_exists(fname):
    out_dir = os.path.dirname(fname)
    if not os.path.exists(out_dir):
        try:
            os.makedirs(out_dir)
        except:
            pass


class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)


class NumpyDecoder(json.JSONDecoder):
    def decode(self, s, **kwargs):
        if s == "null":
            return np.nan
        return super(NumpyDecoder, self).decode(s, **kwargs)
