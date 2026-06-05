import re
path = r"C:\Users\Maria Oktavia\Documents\Bot Trading\app.py"
content = open(path, encoding="utf-8").read()

# Remove duplicate index function
old = """@login_required
def index():
    return render_template("Index.html")


@app.route("/login"""
new = """@app.route("/login"""
if old in content:
    content = content.replace(old, new, 1)
    open(path, "w", encoding="utf-8").write(content)
    print("Duplicate index removed")
else:
    print("No duplicate found")
