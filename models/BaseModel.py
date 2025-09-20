import csv
import os

class BaseModel:
    def __init__(self, filename):
        self.filename = filename
        self.data = []
        self.load_data()
        
    def load_data(self):
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r', newline='', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    self.data = list(reader)
            except:
                self.data = []
        else:
            self.data = []
        return self.data
        
    def save_data(self):
        if hasattr(self, 'fieldnames') and self.fieldnames and self.data:
            with open(self.filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=self.fieldnames)
                writer.writeheader()
                writer.writerows(self.data)
                
    def get_next_id(self):
        if not self.data:
            return 1
        ids = [int(item['id']) for item in self.data if 'id' in item and item['id'].isdigit()]
        return max(ids) + 1 if ids else 1