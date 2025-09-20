from models.BaseModel import BaseModel
from config import Config

class UserModel(BaseModel):
    def __init__(self):
        super().__init__(Config.USERS_FILE)
        self.fieldnames = ['id', 'username', 'password', 'balance']
        
    def create_sample_data(self):
        self.data = []
        for i in range(10):
            self.data.append({
                'id': str(i + 1),
                'username': f'user{i+1}',
                'password': f'pass{i+1}',
                'balance': str(Config.DEFAULT_USER_BALANCE)
            })
        self.save_data()
        
    def authenticate(self, username, password):
        for user in self.data:
            if user['username'] == username and user['password'] == password:
                return user
        return None
        
    def update_balance(self, user_id, amount):
        for user in self.data:
            if user['id'] == user_id:
                current_balance = int(user['balance'])
                if current_balance >= amount:
                    user['balance'] = str(current_balance - amount)
                    self.save_data()
                    return True
        return False