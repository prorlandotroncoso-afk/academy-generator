import requests

url = "https://academiafluent.infinityfree.me/wp-json/wp/v2/users/me"

usuario = "TU_USUARIO"
password = "TU_APPLICATION_PASSWORD"

r = requests.get(
    url,
    auth=(usuario, password)
)

print("STATUS:", r.status_code)
print(r.text)