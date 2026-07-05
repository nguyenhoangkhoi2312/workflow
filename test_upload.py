import requests
files = {'file': ('test.txt', b'hello world', 'text/plain')}
res = requests.post('http://127.0.0.1:8000/api/documents/upload', files=files)
print(res.status_code)
print(res.text)
