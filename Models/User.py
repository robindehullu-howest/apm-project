class User:
    __usercount = 0

    def __init__(self, username: str, email: str, password: str, nickname: str = None):
        self.__username = username
        self.__password = password
        self.__nickname = nickname
        self.__email = email
        User.__usercount += 1

    @property
    def username(self):
        return self.__username

    @property
    def nickname(self):
        return self.__nickname
    
    @property
    def email(self):
        return self.__email

    @property
    def password(self):
        return self.__password

    @staticmethod
    def get_usercount():
        return User.__usercount

    def __str__(self):
        return f'Username: {self.username} - Email: {self.email} - Nickname: {self.nickname} - Password: {self.password}'

    def __eq__(self, other: object) -> bool:
        if isinstance(other, User):
            return (self.username == other.username or self.email == other.email) and self.password == other.password
        return False

    def __del__(self):
        User.__usercount -= 1

    def __setstate__(self, state: dict):
        self.__dict__.update(state)
        User.__usercount += 1