from typing import List, Dict

class User:
    def __init__(self, user_id: int, name: str, username: str, email: str):
        self.id = user_id
        self.name = name
        self.username = username
        self.email = email
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "username": self.username,
            "email": self.email
        }
    
class UserManager:
    def __init__(self):
        self.users: List[User] = []
        self.next_id = 1
    
    def add_user(self, name: str, username: str, email: str) -> User:
        user = User(self.next_id, name, username, email)
        self.users.append(user)
        self.next_id += 1
        return user
    
    def get_user_by_id(self, user_id: int) -> User:
        for user in self.users:
            if user.id == user_id:
                return user
        return None
    
    def get_all_users(self) -> List[User]:
        return self.users
    
    def delete_user(self, user_id: int) -> bool:
        for i, user in enumerate(self.users):
            if user.id == user_id:
                self.users.pop(i)
                return True
        return False

user_manager = UserManager()