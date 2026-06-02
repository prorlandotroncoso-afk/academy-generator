import requests

url = "http://academiafluent.infinityfree.me/wp-json/academy/v1/test"

headers = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json"
}

try:
    r = requests.get(
        url,
        headers=headers,
        timeout=30
    )

    print("STATUS:", r.status_code)
    print(r.text[:500])

except Exception as e:
    print("ERROR:")
    print(e)