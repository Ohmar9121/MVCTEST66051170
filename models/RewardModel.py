from models.BaseModel import BaseModel
import random
from config import Config
from models.ProjectModel import ProjectModel

class RewardModel(BaseModel):
    def __init__(self):
        super().__init__(Config.REWARDS_FILE)
        self.fieldnames = ['id', 'project_id', 'name', 'min_amount', 'quota']
        
    def create_sample_data(self):
        self.data = []
        project_model = ProjectModel()
        projects = project_model.load_data()
        
        for project in projects:
            for i in range(random.randint(2, 3)):
                min_amount = random.randint(100, 1000) * (i + 1)
                quota = random.randint(5, 20)
                
                self.data.append({
                    'id': str(self.get_next_id()),
                    'project_id': project['id'],
                    'name': f'Tier {i+1} Reward',
                    'min_amount': str(min_amount),
                    'quota': str(quota)
                })
        self.save_data()
        
    def get_rewards_for_project(self, project_id):
        return [reward for reward in self.data if reward['project_id'] == project_id]
        
    def decrease_quota(self, reward_id):
        for reward in self.data:
            if reward['id'] == reward_id and int(reward['quota']) > 0:
                reward['quota'] = str(int(reward['quota']) - 1)
                self.save_data()
                return True
        return False