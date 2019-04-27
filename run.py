import config
import subprocess
import os

environment = os.environ.copy()
environment["FLASK_APP"] = config.FLASK_APP
environment["FLASK_ENV"] = config.FLASK_ENV

subprocess.run(["flask", "run"], env=environment)