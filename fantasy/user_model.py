from flask_login import UserMixin


class User(UserMixin):
    def __init__(self, id, email, display_name, password, role):
        self.id = id
        self.email = email
        self.display_name = display_name
        self.password = password
        self.role = role

    def is_adventurer(self):
        return self.role == "adventurer"

    def is_guild_master(self):
        return self.role == "guild_master"

    def is_council(self):
        return self.role == "council"
