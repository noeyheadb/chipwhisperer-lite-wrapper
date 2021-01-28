import numpy as np


class CWTrace:
    def __init__(self, trace):
        self.key: str = trace.key.hex().upper()
        self.textin: str = trace.textin.hex().upper()
        self.textout: str = trace.textout.hex().upper()
        self.trace: np.ndarray = trace.wave
        pass

    def __repr__(self) -> str:
        return f"<CW-w-Trace samples: {self.trace.shape[0]} " \
               f"key: {self.key} textin: {self.textin} textout: {self.textout}>"
    pass
