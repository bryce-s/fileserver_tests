import sys
import os
import subprocess
import re
from sty import fg
import time

def get_fs_output():
    print(open("../fs_output").read())


def start_fileserver(port: str = "1902"):
    print(fg.blue + " >> Starting the fileserver..." + fg.rs)
    cp = subprocess.run("sh start_fs.sh", shell=True, text=True)
    time.sleep(1) # make sure FS has started before going on..
    if cp.returncode != 0:
        print(fg.red + "FS failed to start! Output" + fg.rs + open("../fs_output").read() + fg.rs)
    if not os.path.isfile('../fs_output'):
        print(fg.red + "fs_output was never generated, fs probably didn't start" + fg.rs)
        exit(1)



def kill_fileserver():
    print(fg.blue + " >> Killing the fileserver..." + fg.rs)
    cp = subprocess.run("sh kill_all_fs.sh", capture_output=True, text=True, shell=True)
    cp2 = subprocess.run("../createfs", capture_output=True, text=True, shell=True)
    time.sleep(1)

def check_fs_for_errors():
    fs_output = open("../fs_output").read()
    res = list()
    res.extend(re.findall(r'Segment', fs_output))
    res.extend(re.findall(r'exit', fs_output))
    res.extend(re.findall(r'Assert', fs_output))
    res.extend(re.findall(r'assert', fs_output))
    res.extend(re.findall(r'Bus error', fs_output))

    if len(res) > 0:
        print(fg.red + "FS errors detected. Output: " + fs_output)
        return 1
    return 0




def diff_check(correct: str, output: str, message: str, target: str, correct_fs_output: str, fs_output: str):
    if (correct != output):
        print(fg.red + target + " FS output differs: " + fg.rs)        
        print(fg.green + "correct: \n" + fg.rs + correct)
        print(fg.red+ "incorrect: \n" + fg.rs + output)        
        kill_fileserver()
        return 1
    return 0

def run_test_with_restart(target: str, port: str = 1902, check_filesys: bool = True, check_client: bool = False):
    print("---> Running " + target + ":")
    start_fileserver()
    if check_fs_for_errors() != 0:
        kill_fileserver()
        return 1

    try:
        client = subprocess.run("cd .. && ./" + target + " localhost " + str(port) + " 2>&1", timeout=2, shell=True, text=True, capture_output=True)
    except subprocess.TimeoutExpired:
        print(fg.red + "A call timed out.. Output" + fg.rs)
        print(fg.red + "fs output: ")
        get_fs_output()
        kill_fileserver()         
        return 1

    if client.returncode != 0:
        print(fg.red + target + " exited with error!")
        print(fg.red + "incorrect output:" + fg.rs)
        print(str(client.stdout))
        kill_fileserver()
        return 1

    if check_client:
        correct_client_output = "./app_output/" + target + ".out"
        if not os.path.isfile(correct_client_output):
            print(fg.red + "no correct client program .out found in " + correct_client_output + fg.rs)
            print(str(client.stdout))   
        if diff_check(open(correct_client_output).read(), str(client.stdout), " Client output differs: ", target, correct_fs_output, fs_output) == 1:
            return 1

    if check_fs_for_errors() != 0:
        kill_fileserver()
        return 1

    if check_filesys:    
        fsproc = subprocess.run("cat ../fs_output | grep -a @@@", shell=True, text=True, capture_output=True)
        fs_output = str(fsproc.stdout)
        correct_fs_output = "./fs_output/" + target + ".out"
        if not os.path.isfile(correct_fs_output):
            print(fg.red + "no correct filesystem output found in" + correct_fs_output + fg.rs)
            kill_fileserver()
            return 1
        if diff_check(open(correct_fs_output).read(), fs_output, " FS output differs: ", target, correct_fs_output, fs_output) == 1:
            return 1
    print(fg.green + "Test " + target + " passed!") 
    kill_fileserver()
    return 0
 
    

    kill_fileserver()


def run_all_tests(tests: list):
    print("exec targets: " + str(tests))
    total_failed = 0
    total_tests = 0
    for test in tests:
        if run_test_with_restart(test) == 1:
            total_failed += 1
        total_tests += 1
    print("ran " + str(total_tests) + " tests, there were " + str(total_failed) + " failures.")


def build_project():
    """builds the project and returns our list of execution targets"""
    makeFileStr = open("../Makefile", "r").read()
    compile_targets = re.findall("\w+:", makeFileStr)
    compile_targets.remove("all:")
    compile_targets.remove("clean:")
    compile_targets.remove("FS_SOURCES:")
    compile_targets.remove("o:")
    compile_targets.remove("o:")
    compile_targets.remove("fss:")

    print(compile_targets)
    for target in compile_targets:
        cp = subprocess.run("cd .. && make " + target[0:len(target)-1], shell=True, capture_output=True, text=True)
        if cp.returncode != 0:
            print(fg.red + "make failed in " + target[0:len(target)-1] + ", output: " +fg.rs)
            print(str(cp.stderr))
            exit(1)
        else:
            print(fg.green + target + " built! " + fg.rs)
    new_targets = list()
    # we'll just transfer over real quick
    for target in compile_targets:
        if target != "fs:" and target != "fss:":
            new_targets.append(target[0:len(target)-1])    
    return new_targets


def main():
    # ensure CWD is always /tests, so we can run the script from anywhere.
    abspath = os.path.abspath(__file__)
    dname = os.path.dirname(abspath)
    os.chdir(dname)
    exec_targets = build_project()
    kill_fileserver()
    run_all_tests(exec_targets)
    
    
main()