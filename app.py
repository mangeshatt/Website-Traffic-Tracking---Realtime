from flask import Flask, request
import sqlite3
from datetime import datetime
import hashlib

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('traffic.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS visits 
                 (timestamp TEXT, ip_hash TEXT, user_agent TEXT, path TEXT)''')
    c.execute('''CREATE INDEX IF NOT EXISTS idx_ip ON visits(ip_hash)''')
    c.execute('''CREATE INDEX IF NOT EXISTS idx_date ON visits(timestamp)''')
    conn.commit()
    conn.close()

init_db()

def hash_ip(ip):
    return hashlib.sha256(ip.encode()).hexdigest()[:16]

@app.route('/track')
def track():
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    ip_hash = hash_ip(ip)
    timestamp = datetime.now().isoformat()
    user_agent = request.headers.get('User-Agent', 'Unknown')
    path = request.path
    
    conn = sqlite3.connect('traffic.db')
    c = conn.cursor()
    c.execute("INSERT INTO visits VALUES (?, ?, ?, ?)", 
              (timestamp, ip_hash, user_agent, path))
    conn.commit()
    conn.close()
    return 'OK', 200

@app.route('/')
def index():
    return '''
    <html><head><title>Traffic Active</title></head>
    <body><h1>Tracker Active</h1>
    <script>fetch("/track"); setInterval(()=>fetch("/track"),30000);</script>
    </body></html>'''

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
