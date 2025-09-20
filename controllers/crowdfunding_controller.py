from models.ProjectModel import ProjectModel
from models.RewardModel import RewardModel
from models.PledgeModel import PledgeModel
from models.UserModel import UserModel
from datetime import datetime

class CrowdfundingController:
    def __init__(self):
        self.project_model = ProjectModel()
        self.reward_model = RewardModel()
        self.pledge_model = PledgeModel()
        self.user_model = UserModel()
        
    def initialize_sample_data(self):
        self.project_model.create_sample_data()
        self.reward_model.create_sample_data()
        self.user_model.create_sample_data()
        
    def get_project_details(self, project_id):
        project = None
        for p in self.project_model.data:
            if p['id'] == project_id:
                project = p
                break
                
        if not project:
            return None
            
        rewards = self.reward_model.get_rewards_for_project(project_id)
        pledges = self.pledge_model.get_pledges_for_project(project_id)
        
        successful_pledges = len([p for p in pledges if p['status'] == 'success'])
        rejected_pledges = len([p for p in pledges if p['status'] == 'rejected'])
        
        # Get contributors
        contributors = self.get_contributors_for_project(project_id)
        
        # Calculate funding status - FIXED LOGIC
        current_amount = int(project['current'])
        target_amount = int(project['target'])
        deadline = datetime.strptime(project['deadline'], "%Y-%m-%d")
        now = datetime.now()
        
        # CORRECT LOGIC: Successful if reached target, failed if deadline passed without reaching target
        if current_amount >= target_amount:
            funding_status = "successful"
        elif deadline < now:
            funding_status = "failed"
        else:
            funding_status = "active"
        
        return {
            'project': project,
            'rewards': rewards,
            'pledges': pledges,
            'contributors': contributors,
            'successful_pledges': successful_pledges,
            'rejected_pledges': rejected_pledges,
            'funding_status': funding_status,
            'target_reached': current_amount >= target_amount
        }
        
    # In controllers/crowdfunding_controller.py - Update get_project_details method
    def get_project_details(self, project_id):
        project = None
        for p in self.project_model.data:
            if p['id'] == project_id:
                project = p
                break
            
        if not project:
            return None
            
        rewards = self.reward_model.get_rewards_for_project(project_id)
        pledges = self.pledge_model.get_pledges_for_project(project_id)
        
        successful_pledges = len([p for p in pledges if p['status'] == 'success'])
        rejected_pledges = len([p for p in pledges if p['status'] == 'rejected'])
        
        # Get contributors
        contributors = self.get_contributors_for_project(project_id)
        
        # Calculate funding status
        current_amount = int(project['current'])
        target_amount = int(project['target'])
        from datetime import datetime
        deadline = datetime.strptime(project['deadline'], "%Y-%m-%d")
        now = datetime.now()
        
        funding_status = "active"
        if current_amount >= target_amount:
            funding_status = "successful"
        elif deadline < now:
            funding_status = "failed"
        
        return {
            'project': project,
            'rewards': rewards,
            'pledges': pledges,
            'contributors': contributors,
            'successful_pledges': successful_pledges,
            'rejected_pledges': rejected_pledges,
            'funding_status': funding_status,
            'target_reached': current_amount >= target_amount
        }
        
    def make_pledge(self, user_id, project_id, reward_id, amount):
        # Find user
        user = None
        for u in self.user_model.data:
            if u['id'] == user_id:
                user = u
                break
        if not user:
            self.pledge_model.create_pledge(user_id, project_id, reward_id, amount, 'rejected')
            return {'success': False, 'message': 'User not found'}
        
        # Check balance
        if int(user['balance']) < amount:
            self.pledge_model.create_pledge(user_id, project_id, reward_id, amount, 'rejected')
            return {'success': False, 'message': 'Insufficient balance'}
        
        # Find project
        project = None
        for p in self.project_model.data:
            if p['id'] == project_id:
                project = p
                break
        if not project:
            self.pledge_model.create_pledge(user_id, project_id, reward_id, amount, 'rejected')
            return {'success': False, 'message': 'Project not found'}
        
        # Check if project is still active
        project_details = self.get_project_details(project_id)
        if project_details['funding_status'] != 'active':
            self.pledge_model.create_pledge(user_id, project_id, reward_id, amount, 'rejected')
            return {'success': False, 'message': 'Project is no longer accepting pledges'}
        
        
        # Check deadline
        deadline = datetime.strptime(project['deadline'], "%Y-%m-%d")
        if deadline < datetime.now():
            self.pledge_model.create_pledge(user_id, project_id, reward_id, amount, 'rejected')
            return {'success': False, 'message': 'Project deadline has passed'}
        
        # Check reward if selected
        if reward_id and reward_id != 'None' and reward_id != '':
            reward = None
            for r in self.reward_model.data:
                if r['id'] == reward_id and r['project_id'] == project_id:
                    reward = r
                    break
            
            if not reward:
                self.pledge_model.create_pledge(user_id, project_id, reward_id, amount, 'rejected')
                return {'success': False, 'message': 'Invalid reward'}
            
            if int(reward['quota']) <= 0:
                self.pledge_model.create_pledge(user_id, project_id, reward_id, amount, 'rejected')
                return {'success': False, 'message': 'Reward quota exceeded'}
            
            if amount < int(reward['min_amount']):
                self.pledge_model.create_pledge(user_id, project_id, reward_id, amount, 'rejected')
                return {'success': False, 'message': f'Amount below minimum ${reward["min_amount"]}'}
        
        # Process successful pledge
        if not self.user_model.update_balance(user_id, amount):
            self.pledge_model.create_pledge(user_id, project_id, reward_id, amount, 'rejected')
            return {'success': False, 'message': 'Failed to update balance'}
        
        self.project_model.update_funding(project_id, amount)
        
        if reward_id and reward_id != 'None' and reward_id != '':
            self.reward_model.decrease_quota(reward_id)
        
        pledge = self.pledge_model.create_pledge(user_id, project_id, reward_id, amount, 'success')
        return {'success': True, 'message': 'Pledge successful'}
        
    def authenticate_user(self, username, password):
        return self.user_model.authenticate(username, password)
        
    def get_stats(self):
        all_pledges = self.pledge_model.get_all_pledges()
        successful = len([p for p in all_pledges if p['status'] == 'success'])
        rejected = len([p for p in all_pledges if p['status'] == 'rejected'])
        return successful, rejected
    
    def get_project_status_counts(self):
        from datetime import datetime
        
        failed_count = 0
        successful_count = 0
        active_count = 0
        
        for project in self.project_model.data:
            current_amount = int(project['current'])
            target_amount = int(project['target'])
            deadline = datetime.strptime(project['deadline'], "%Y-%m-%d")
            now = datetime.now()
            
            # - Successful if reached target (regardless of deadline)
            # - Failed if deadline passed AND didn't reach target
            # - Active if deadline not passed AND didn't reach target
            if current_amount >= target_amount:
                successful_count += 1
            elif deadline < now:  # Deadline passed but didn't reach target
                failed_count += 1
            else:  # Still active and hasn't reached target
                active_count += 1
        
        return {
            'failed': failed_count,
            'successful': successful_count,
            'active': active_count
        }
        
    # In controllers/crowdfunding_controller.py - Add this method
    def get_contributors_for_project(self, project_id):
        """Get list of users who contributed to a project with total amounts"""
        contributors_dict = {}
        project_pledges = [p for p in self.pledge_model.data if p['project_id'] == project_id and p['status'] == 'success']
        
        for pledge in project_pledges:
            user_id = pledge['user_id']
            # Find user details
            for user in self.user_model.data:
                if user['id'] == user_id:
                    if user_id not in contributors_dict:
                        contributors_dict[user_id] = {
                            'username': user['username'],
                            'total_amount': 0,
                            'pledges': []
                        }
                    
                    contributors_dict[user_id]['total_amount'] += int(pledge['amount'])
                    contributors_dict[user_id]['pledges'].append({
                        'amount': pledge['amount'],
                        'timestamp': pledge['timestamp']
                    })
                    break
        
        # Convert to list format for template
        contributors = []
        for user_id, data in contributors_dict.items():
            contributors.append({
                'username': data['username'],
                'total_amount': data['total_amount'],
                'pledge_count': len(data['pledges']),
                'latest_pledge': max(data['pledges'], key=lambda x: x['timestamp']) if data['pledges'] else None
            })
        
        # Sort by total amount descending
        contributors.sort(key=lambda x: x['total_amount'], reverse=True)
        return contributors
    
        # In controllers/crowdfunding_controller.py - Add this method
    def get_projects(self, search=None, category=None, sort_by='deadline'):
        # Load fresh data
        projects = self.project_model.load_data()
        
        # Apply search filter
        if search:
            projects = [p for p in projects if search.lower() in p['name'].lower()]
        
        # Apply category filter
        if category:
            projects = [p for p in projects if p['category'] == category]
        
        # Apply sorting
        if sort_by == 'deadline':
            from datetime import datetime
            projects.sort(key=lambda x: datetime.strptime(x['deadline'], "%Y-%m-%d"))
        elif sort_by == 'newest':
            projects.sort(key=lambda x: x['id'], reverse=True)
        elif sort_by == 'most_funded':
            projects.sort(key=lambda x: int(x['current']), reverse=True)
        
        return projects