import requests

url = "http://academiafluent.infinityfree.me/wp-json/wp/v2/posts"

headers = {
    "User-Agent": "Mozilla/5.0"
}

try:
    r = requests.get(
        url,
        headers=headers,
        timeout=20
    )

    print("STATUS:", r.status_code)
    print(r.text[:300])

except Exception as e:
    print("ERROR:")
    print(e)