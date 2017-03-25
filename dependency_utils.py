import sys
import os

def add_external_libs(base, libs):
    sys.path.append(os.path.dirname(__file__))
    external_path = os.path.join(os.path.dirname(__file__), base)

    for name in libs:
        sys.path.append(os.path.join(external_path, name))
