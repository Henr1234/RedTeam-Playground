from flask import Flask, request, redirect, session, render_template_string
import sqlite3, os

app = Flask(__name__)
app.secret_key = "vulnerable_secret"

UPLOAD_FOLDER = "uploads"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# --------- DB Init ----------
def init_db():
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            password TEXT,
            message TEXT,
            role TEXT DEFAULT 'user'
        )
    """)
    # default admin
    c.execute("INSERT OR IGNORE INTO users (id, username, password, role) VALUES (1,'admin','admin','admin')")
    conn.commit()
    conn.close()

init_db()

# --------- Base Layout with placeholder ---------
base_html = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Vulnerable Demo App</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="bg-light">
<nav class="navbar navbar-expand-lg navbar-dark bg-dark mb-4">
  <div class="container-fluid">
    <a class="navbar-brand" href="/">🔥 VulnApp by Lavish /a>
    <div class="collapse navbar-collapse">
      <ul class="navbar-nav ms-auto">
        {% if 'user' in session %}
          <li class="nav-item"><a class="nav-link" href="/profile">Profile</a></li>
          <li class="nav-item"><a class="nav-link" href="/search">Search</a></li>
          <li class="nav-item"><a class="nav-link" href="/upload">Upload</a></li>
          <li class="nav-item"><a class="nav-link" href="/logout">Logout</a></li>
        {% else %}
          <li class="nav-item"><a class="nav-link" href="/login">Login</a></li>
          <li class="nav-item"><a class="nav-link" href="/signup">Signup</a></li>
        {% endif %}
      </ul>
    </div>
  </div>
</nav>
<div class="container">
  {{ content|safe }}
</div>
</body>
</html>
"""

# ---------- Helper to render ----------
def render_page(content, **kwargs):
    return render_template_string(base_html, content=content, **kwargs)

# ---------- Home ----------
@app.route("/")
def home():
    if "user" in session:
        c = f"<h1>Welcome back, {session['user']} 👋</h1>"
    else:
        c = "<h1>Welcome to VulnApp 👋</h1><p>Please login or signup</p>"
    return render_page(c)

# ---------- Signup (SQLi vulnerable) ----------
@app.route("/signup", methods=["GET","POST"])
def signup():
    if request.method=="POST":
        u=request.form["username"]; p=request.form["password"]
        conn=sqlite3.connect("users.db"); c=conn.cursor()
        c.execute(f"INSERT INTO users (username,password) VALUES ('{u}','{p}')") # vuln
        conn.commit(); conn.close()
        return redirect("/login")
    c = """
    <h2>Signup</h2>
    <form method="post" class="w-50">
      <input class="form-control mb-2" name="username" placeholder="Username">
      <input class="form-control mb-2" type="password" name="password" placeholder="Password">
      <button class="btn btn-primary">Signup</button>
    </form>
    """
    return render_page(c)

# ---------- Login (SQLi vulnerable) ----------
@app.route("/login", methods=["GET","POST"])
def login():
    if request.method=="POST":
        u=request.form["username"]; p=request.form["password"]
        conn=sqlite3.connect("users.db"); c=conn.cursor()
        c.execute(f"SELECT * FROM users WHERE username='{u}' AND password='{p}'") # vuln
        user=c.fetchone(); conn.close()
        if user:
            session["user"]=u; return redirect("/")
        else:
            return "Invalid creds!"
    c = """
    <h2>Login</h2>
    <form method="post" class="w-50">
      <input class="form-control mb-2" name="username" placeholder="Username">
      <input class="form-control mb-2" type="password" name="password" placeholder="Password">
      <button class="btn btn-success">Login</button>
    </form>
    """
    return render_page(c)

# ---------- Profile (Stored XSS + IDOR) ----------
@app.route("/profile", methods=["GET","POST"])
def profile():
    if "user" not in session: return redirect("/login")
    conn=sqlite3.connect("users.db"); c=conn.cursor()
    if request.method=="POST":
        msg=request.form["message"]
        c.execute(f"UPDATE users SET message='{msg}' WHERE username='{session['user']}'") # vuln
        conn.commit()
    c.execute(f"SELECT message FROM users WHERE username='{session['user']}'")
    row=c.fetchone(); msg=row[0] if row else ""; conn.close()
    html=f"""
    <h2>Profile of {session['user']}</h2>
    <form method="post" class="w-50">
      <input class="form-control mb-2" name="message" value="{msg}">
      <button class="btn btn-warning">Update</button>
    </form>
    <p>Your message: {msg}</p>
    <hr>
    <a href="/profile/admin" class="btn btn-danger">Try Broken Access Control</a>
    """
    return render_page(html)

@app.route("/profile/<username>")
def profile_idor(username):
    if "user" not in session: return redirect("/login")
    conn=sqlite3.connect("users.db"); c=conn.cursor()
    c.execute(f"SELECT message FROM users WHERE username='{username}'")
    row=c.fetchone(); msg=row[0] if row else "No msg"; conn.close()
    html=f"""
    <h2>Profile of {username}</h2>
    <p>{msg}</p>
    <p class="text-danger">[Broken Access Control] Anyone can view!</p>
    """
    return render_page(html)

# ---------- Search (Reflected XSS) ----------
@app.route("/search")
def search():
    q=request.args.get("q","")
    html=f"""
    <h2>Search</h2>
    <form method="get" class="w-50">
      <input class="form-control mb-2" name="q" value="{q}">
      <button class="btn btn-info">Search</button>
    </form>
    <p>Results for: {q}</p>
    """
    return render_page(html)

# ---------- File Upload ----------
@app.route("/upload", methods=["GET","POST"])
def upload():
    if "user" not in session: return redirect("/login")
    if request.method=="POST":
        f=request.files["file"]; path=os.path.join(app.config["UPLOAD_FOLDER"], f.filename)
        f.save(path); return f"Uploaded: {f.filename}"
    html="""
    <h2>File Upload</h2>
    <form method="post" enctype="multipart/form-data" class="w-50">
      <input type="file" name="file" class="form-control mb-2">
      <button class="btn btn-secondary">Upload</button>
    </form>
    """
    return render_page(html)

# ---------- Logout ----------
@app.route("/logout")
def logout():
    session.pop("user",None)
    return redirect("/")

if __name__=="__main__":
    app.run(debug=True)
