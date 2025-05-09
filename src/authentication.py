from classes import User


def authenticate_user(username, password):
    users = User.from_csv('./Credentials.csv')
    user = users.get(username)
    if user is None or not user.authenticate(password):
        print("Invalid credentials. Access denied.")
        return None
    return user
