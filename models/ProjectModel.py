from models.BaseModel import BaseModel
from datetime import datetime, timedelta
import random
from config import Config

class ProjectModel(BaseModel):
    def __init__(self):
        super().__init__(Config.PROJECTS_FILE)
        self.fieldnames = ['id', 'name', 'target', 'deadline', 'current', 'category']
        
    def create_sample_data(self):
        self.data = []
        for i in range(8):
            project_id = str(10000000 + i)
            target = random.randint(5000, 50000)
            days = random.randint(10, 60)
            deadline = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")
            category = random.choice(Config.PROJECT_CATEGORIES)
            
            self.data.append({
                'id': project_id,
                'name': f'Project {i+1} - {category}',
                'target': str(target),
                'deadline': deadline,
                'current': '0',
                'category': category
            })
        self.save_data()
        
    def update_funding(self, project_id, amount):
        self.load_data() 
        for project in self.data:
            if project['id'] == project_id:
                project['current'] = str(int(project['current']) + amount)
                break
        self.save_data()