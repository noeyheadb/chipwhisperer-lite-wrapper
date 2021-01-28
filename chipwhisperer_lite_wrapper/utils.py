import os
import chipwhisperer as cw
import numpy as np
import matplotlib.pyplot as plt
import seaborn
from typing import Optional
seaborn.set()


def cw_lite_firmware_update_automatically():
    scope = cw.scope()
    _ = cw.target(scope)
    programmer = cw.SAMFWLoader(scope=scope)
    programmer.auto_program()
    pass


def visualization_single_trace(wave: np.ndarray) -> plt.Figure:
    trace_img: plt.Figure = plt.figure(figsize=(8.0, 4.5))
    trace_axes: plt.Axes = trace_img.add_subplot(1, 1, 1)
    trace_axes.set_title(f"Captured trace")
    trace_axes.set_xlabel("Index of traces")
    trace_axes.set_ylabel(f"Voltage")
    trace_axes.plot(wave, linewidth=0.5)
    trace_img.show()
    return trace_img


def check_and_reformat_dir(target_dir: Optional[str]) -> str:
    if target_dir is None:
        return ""
    target_dir.replace("/", os.sep)
    target_dir.replace("\\", os.sep)

    if not os.path.exists(target_dir):
        os.makedirs(target_dir, exist_ok=True)

    if not os.path.isdir(target_dir):
        raise RuntimeError(f"[Error] \"{target_dir}\" does not exist.")

    if not target_dir.endswith(os.sep):
        target_dir = target_dir + os.sep

    return target_dir
