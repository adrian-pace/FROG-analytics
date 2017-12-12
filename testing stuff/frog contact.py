import requests

r = requests.post("http://127.0.0.1:5000", json={'pad_names': ["editor2"]})
print(r)

r = requests.get("http://127.0.0.1:5000")
print(r.text)

r = requests.post("http://127.0.0.1:5000", json={'regex': "^/ac-textarea/default"})
print(r)
