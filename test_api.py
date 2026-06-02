import requests

url = "http://academiafluent.infinityfree.me/wp-json/wp/v2/lp_question"

try:
    r = requests.get(url, timeout=20)

    print("STATUS:", r.status_code)
    print()
    print(r.text[:500])

except Exception as e:
    print("ERROR:")
    print(e)