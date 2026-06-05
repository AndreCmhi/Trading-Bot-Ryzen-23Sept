import re
path = r"C:\Users\Maria Oktavia\Documents\Bot Trading\app.py"
content = open(path, encoding="utf-8").read()
lines = content.split('\n')

seen_funcs = set()
remove_next = False
new_lines = []

for i, line in enumerate(lines):
    # Check if this line starts a duplicate function
    match = re.match(r'def ([a-z_]+)\(', line)
    if match:
        func_name = match.group(1)
        if func_name in seen_funcs:
            # Skip this function and its body until next def or @
            remove_next = True
            print(f"Removing duplicate: {func_name}")
        else:
            seen_funcs.add(func_name)
            new_lines.append(line)
    elif remove_next:
        # Skip until we hit a def or @ (start of next function/decorator)
        if line.strip().startswith('@') or re.match(r'def ', line):
            remove_next = False
            new_lines.append(line)
    else:
        new_lines.append(line)

open(path, "w", encoding="utf-8").write('\n'.join(new_lines))
print("Done removing duplicates")
