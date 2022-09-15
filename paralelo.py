import subprocess
import shlex

subprocess.run(shlex.split("python3 fabrica.py -n 1 -p 140 141 142 python3 fabrica.py -n 2 -p 143 144 145"))
#subprocess.call("ps")