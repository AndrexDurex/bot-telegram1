import socket
import sys

import logging
import os
from bioagent.startup import prepare_credentials
from bioagent.bot import run

if __name__ == "__main__":
    print("--- STARTUP BIOAGENT V3.0 ---", flush=True)
    prepare_credentials()
    sys.stdout.flush()
    run()
