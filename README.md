# Quick start (on unix)
````
# if on caen:
module load python/3.7

# create python env
# use python or python3, whichever happens to be mapped to python 3.
python(3?) -m venv env
#activate python env
source env/bin/activate
# install pretty colors (only must do this once..)
pip install sty

# run all tests:
`python tests/controller.py`
````




# Adding correct files
```
save an app output like this:
./test_session_basic localhost 1902 > tests/app_output/test_session_basic.out

save fs output like this:
./fs 1902 < passwords | grep -a --line-buffered  @@@ > tests/fs_output/test_session_basic.out
```

