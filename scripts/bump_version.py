#!/usr/bin/env python3
import re, sys

path = "circleci_trigger/__init__.py"
data = open(path).read()
m = re.search(r"__version__ = ['\"](.+?)['\"]", data)
ver = m.group(1)
major, minor, patch = map(int, ver.split("."))
patch += 1
new = f"{major}.{minor}.{patch}"
open(path,"w").write(f"__version__ = '{new}'\n")
print(new)
