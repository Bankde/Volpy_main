# pickle_benchmarker

Run the test

```
python test.py
```

The raw result will be in result.json in json format.  

This testsuite uses Python subprocess to run so make sure the environment is correct (e.g. Python version, dill, cloudpickle) during the test.  
If run in the IDE, make sure the IDE uses the correct Python version throughout the test. To check the environment, run the script
```
python env_check.py
```

To include benchmark (speed/size) test, set the environment variable before running the test.
```
export BENCHMARK=1
```

Turn raw result (result.json) into summary file using the script:
```
# For object support (output to stdout)
python summary.py
# Same as above but output to file
python summary.py -o summary_obj.txt

# For speed
python summary.py --data time -o summary_time.txt
# For size
python summary.py --data size -o summary_size.txt

# Use input from some_file.json instead of default (result.json)
python summary.py -i some_file.json -o summary_size.txt
```

