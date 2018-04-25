import subprocess
from subprocess import PIPE

p = subprocess.Popen('req.bat', shell=True, stdout=PIPE, stderr=PIPE)
stdout, stderr = p.communicate()
