import os
from pathlib import Path

home = Path.home()

python_dir = f"{home}/AppData/Local/Programs/Python/Python38-32/python.exe"
pckg_dir = f"{home}/Documents/projets/Models"

os.system(" & ".join([
    f"cd {pckg_dir}",
    f"{python_dir} setup.py sdist bdist_wheel",
    f'{python_dir} -m twine upload --repository testpypi dist/*'
]))
