path = r"C:\Users\Maria Oktavia\Documents\Bot Trading\app.py"
content = open(path, encoding="utf-8").read()

# Find all function definitions
import re
funcs = re.findall(r'def ([a-z_]+)\(', content)
from collections import Counter
dups = [f for f, c in Counter(funcs).items() if c > 1]
print("Duplicates:", dups)
