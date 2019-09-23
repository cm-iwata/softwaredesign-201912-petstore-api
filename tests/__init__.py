import os
import sys
from pathlib import Path

tests_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = str(Path(f'{tests_dir}/../src').resolve())
sys.path.append(src_dir)
