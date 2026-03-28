import urllib.request
try:
    r = urllib.request.urlopen('http://127.0.0.1:5000/health')
    print("SERVER IS UP:", r.read())
except Exception as e:
    print("SERVER NOT RUNNING:", e)
