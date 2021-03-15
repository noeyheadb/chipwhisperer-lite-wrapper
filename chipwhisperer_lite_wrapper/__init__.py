__all__ = ['CWLiteWrapper', 'CWTrace', 'visualization_single_trace', 'cw_lite_firmware_update_automatically']


# #######################################################################################
# #   If you want to use chipwhisperer submodule in this repository, uncomment below.   #
# #######################################################################################

# import sys
# import os
# sys.path.insert(0, os.path.dirname(os.path.abspath(os.path.dirname(
#     "./newaetech-chipwhisperer/software/chipwhisperer/__init__.py"))))

# #######################################################################################

from .cw_lite_wrapper import CWLiteWrapper
from .cw_trace import CWTrace
from .utils import visualization_single_trace, cw_lite_firmware_update_automatically
