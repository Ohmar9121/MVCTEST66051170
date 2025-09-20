from models.BaseModel import BaseModel
from datetime import datetime
from config import Config

class PledgeModel(BaseModel):
    def __init__(self):
        super().__init__(Config.PLEDGES_FILE)
        self.fieldnames = ['id', 'user_id', 'project_id', 'reward_id', 'amount', 'timestamp', 'status']
        
    def create_pledge(self, user_id, project_id, reward_id, amount, status='success'):
        reward_display = reward_id if reward_id and reward_id != 'None' and reward_id != '' else 'None'
        
        pledge = {
            'id': str(self.get_next_id()),
            'user_id': user_id,
            'project_id': project_id,
            'reward_id': reward_display,
            'amount': str(amount),
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'status': status
        }
        
        self.data.append(pledge)
        self.save_data()
        return pledge
        
    def get_pledges_for_project(self, project_id):
        return [pledge for pledge in self.data if pledge['project_id'] == project_id]
        
    def get_all_pledges(self):
        return self.data