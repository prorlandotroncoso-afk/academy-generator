import requests

url = "http://academiafluent.infinityfree.me/wp-json/wp/v2/posts"

try:
    r = requests.get(url, timeout=20)

    print("STATUS:", r.status_code)
    print(r.text[:500])

except Exception as e:
    print("ERROR:")
    print(e)