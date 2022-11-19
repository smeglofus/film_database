
user = "55,108,10,105"
film_id = "10"
def delete_id(user,film_id):
    konec = user.replace(f",{film_id}","")
    return konec





print(delete_id(user,film_id))

