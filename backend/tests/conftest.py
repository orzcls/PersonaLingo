"""pytest rootdir \u5165\u53e3: \u786e\u4fdd `app` \u5305\u53ef\u88ab\u5bfc\u5165"""
import sys
import os

# \u5c06 backend/ \u52a0\u5165 sys.path,\u4f7f `import app.*` \u5728\u4efb\u4f55\u6d4b\u8bd5\u4f4d\u7f6e\u90fd\u80fd\u5de5\u4f5c
_BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _BACKEND_DIR not in sys.path:
    sys.path.insert(0, _BACKEND_DIR)
