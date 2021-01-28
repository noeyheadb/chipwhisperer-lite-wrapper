from chipwhisperer_lite_wrapper import CWLiteWrapper


# Creating wrapper instance
cw = CWLiteWrapper()
# Connecting CW-Lite
cw.connect()

# Programming compiled hex file (.hex)
cw.xmega_programmer("./output-CW303.hex")

# Setting scope and target detail
cw.set_scope_detail(samples=5000, trigger_mode="rising_edge", offset=300, scale="clkgen_x4")

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
