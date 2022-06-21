import subprocess

subprocess.run(
    "autopep8 --recursive --verbose --in-place --aggressive --exclude venv* .",
    shell=True,
    check=True)
