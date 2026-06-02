import requests

url = "http://academiafluent.infinityfree.me/wp-json/wp/v2/users/me"

r = requests.get(
    url,
    auth=("TU_USUARIO_WORDPRESS", "TU_PASSWORD_WORDPRESS")
)

print(r.status_code)
print(r.text)