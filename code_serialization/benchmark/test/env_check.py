#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys
import subprocess
import dill, cloudpickle, pickle

python_version = str(hex(sys.hexversion))
dill_version = dill.__version__
cloudpickle_version = cloudpickle.__version__

print ("\nModule information:\n")
print (f"\t{'Python version:':<30}{python_version}")
print (f"\t{'dill version:':<30}{dill_version}")
print (f"\t{'cloudpickle version:':<30}{cloudpickle_version}")

main_python_path = sys.executable
sub_python_path = str(subprocess.check_output(['which', 'python']), 'utf-8').strip()
if main_python_path != sub_python_path:
    print("\nALERT: MAIN PROCESS AND SUBPROCESS HAS DIFFERENT EXECUTABLE PATH!\n")
    print (f"\t{'Main Python path:':<30}{main_python_path}")
    print (f"\t{'Subprocess Python path:':<30}{sub_python_path}")

print ()