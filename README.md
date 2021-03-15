# chipwhisperer-lite-wrapper <img src="https://img.shields.io/badge/Code%20line-0.4k-f39fff"></img>
`chipwhisperer-lite-wrapper` is a simple [chipwhisperer](https://github.com/newaetech/chipwhisperer) wrapper, 
which makes it more easy to measure the power traces.
It is only for [`ChipWhisperer®-Lite`](https://rtfm.newae.com/Capture/ChipWhisperer-Lite/), not suitable for other upper and lower models.
(modification required for other models) 
In addition, it only provides the **power trace measurement functions**.

## Requirements
* [chipwhisperer](https://github.com/newaetech/chipwhisperer) (commits up to Jan. 2021)
* numpy
* matplotlib
* seaborn

## Demo
```python
from chipwhisperer_lite_wrapper import CWLiteWrapper


# Creating wrapper instance
cw = CWLiteWrapper()
# Connecting CW-Lite
cw.connect()

# Programming compiled hex file (.hex)
cw.xmega_programmer("./output-CW303.hex")

# Setting scope and target detail
cw.set_scope_detail(samples=5000, trigger_mode="rising_edge", offset=300, scale="clkgen_x4")

# Changing key length  (Default: 128-bit)
# cw.set_key_length(128)

# Setting fixed key
cw.set_fixed_key("FC2A977334D94A8022883DED4D89846E")

# Setting random textin (plain text)
cw.set_random_textin()

# Printing connection status and some information (return dict)
cw.status(verbose=True)

# Measuring a trace
cw.capture_single_trace(visualization=True)

# Measuring multiple traces (trace, textin, textout, key -> ./cw-export/identifier-DATE-trace.npy, ...)
# data = {"trace": traces, "key": keys, "textin": textins, "textout": textouts}
data = cw.capture_multiple_traces(500, "identifier", poi=(1300, 2600))

# Disconnecting cw-lite device
cw.disconnect()

# Disconnecting cw-lite device and resetting internal variables
cw.reset()
```
