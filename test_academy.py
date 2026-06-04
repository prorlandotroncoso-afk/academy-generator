import requests

url = "https://academiafluent.infinityfree.me/wp-json/academy/v1/receive"

data = {
    "title": "QUIZ DESDE PYTHON"
}

try:

    r = requests.post(
        url,
        json=data,
        timeout=30
    )

    print("STATUS:", r.status_code)
    print(r.text)

except Exception as e:

    print("ERROR:")
    print(e)