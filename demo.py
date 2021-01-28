# import wrapper class
from chipwhisperer_lite_wrapper import CWLiteWrapper


# Create wrapper instance
cw = CWLiteWrapper()
# connect CW-Lite
cw.connect()

# Program compiled hex file (.hex)
cw.xmega_programmer("./output-CW303.hex")

# Set scope and target detail
cw.set_scope_detail(samples=5000, trigger_mode="rising_edge", offset=300, scale="clkgen_x4")

# Set fixed key
cw.set_fixed_key("FC2A977334D94A8022883DED4D89846E")

# Set random textin (plain text)
cw.set_random_textin()

# Print connection status and some information (return dict)
cw.status(verbose=True)

# Measure single trace
cw.capture_single_trace(visualization=True)

# Export trace, textin, textout, key numpy array -> ./cw-export/identifier-DATE-trace.npy, ...
cw.capture_multiple_traces(500, "identifier", poi=(1300, 2600))

# Disconnect cw-lite device
cw.disconnect()

# Disconnect cw-lite device and reset internal variables
cw.reset()
