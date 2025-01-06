from pymongo import MongoClient
from bson import ObjectId
import plotly.io as pio
from plotly.graph_objs import Pie, Bar, Figure
from datetime import datetime
import bcrypt

MONGODB_URI = 'mongodb+srv://admin:admin123@cluster0.wkmwh.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0'
client = MongoClient(MONGODB_URI)

class validation():
    def __init__(self) -> None:
        self.db = client.expense_tracker

    def login_validation(self, email, password):
        if email and password:
            user = self.db.users.find_one({"email": email})
            if user:
                if bcrypt.checkpw(password.encode(), user['password_hash']):
                    self.object_id = user.get('_id')
                    return user.get('_id')
                else:
                    return -1
            else:
                return 1
        return 0
          
    def insert_user(self, fullname, email, password):
        try:
            if self.db.users.find_one({"email": email}):
                return 0
            password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
            self.db.users.insert_one({
                "username": fullname,
                "email": email,
                "password_hash": password_hash,
                "created_at": datetime.now()
            })
            return True
        except Exception as e:
            print(e)
            return False
        
    def insert_account(self, account_name ,account_type, balance, user_id):
        try:
            self.db.accounts.insert_one({
                "user_id": ObjectId(user_id),
                "account_name": account_name,
                "account_type": account_type,
                "balance": float(balance),
                "created_at": datetime.now()
            })
            return True
        except Exception as e:
            print(e)
            return False
    
    def retrieve_accounts(self, user_id):
        try:
            accounts = self.db.accounts.find({"user_id": ObjectId(user_id)})
            accounts = list(accounts)
            return accounts
        except Exception as e:
            print(e)
            return []

    def insert_expense(self, user_id, account_id, amount, record_category, date_time, record_description):
        try:
            self.db.records.insert_one({
                "user_id": ObjectId(user_id),
                "type": "expense",
                "account_id": account_id,
                "amount": float(amount),
                "record_category": record_category,
                "date_time": date_time,
                "record_description": record_description if record_description else "" 
            })
            self.db.accounts.update_one({"_id": ObjectId(account_id)}, {"$inc": {"balance": - float(amount)}})
            return True
        except Exception as e:
            print(f"Error inserting expense: {e}")
            return False
        
    def retrieve_expenses(self, user_id):
        try:
            records = self.db.records.find({"$and": [{"user_id": ObjectId(user_id)}, {"type": "expense"}]}).sort([("date_time", -1), ("_id", -1)])
            records = list(records)

            account_ids = list({record['account_id'] for record in records})
            accounts = self.db.accounts.find({"_id": {"$in": account_ids}})
            account_map = {str(account['_id']): account['account_name'] for account in accounts}

            for record in records:
                record['_id'] = str(record['_id'])
                record['user_id'] = str(record['user_id'])
                record['account_id'] = str(record['account_id'])
                
                if 'date_time' in record:
                    if isinstance(record['date_time'], str):
                        record['formatted_date'] = datetime.fromisoformat(record['date_time']).strftime('%b %d, %Y %H:%M')
                    elif isinstance(record['date_time'], datetime):
                        record['formatted_date'] = record['date_time'].strftime('%b %d, %Y %H:%M')
                
                record['account_name'] = account_map.get(record['account_id'], "Deleted Account")
            
            return records

        except Exception as e:
            print(f"Error retrieving records: {e}")
            return []
    
    def insert_income(self, user_id, account_id, amount, record_category, date_time, record_description):
        try:
            self.db.records.insert_one({
                "user_id": ObjectId(user_id),
                "type": "income",
                "account_id": account_id,
                "amount": float(amount),
                "record_category": record_category,
                "date_time": date_time,
                "record_description": record_description if record_description else "" 
            })
            self.db.accounts.update_one({"_id": ObjectId(account_id)}, {"$inc": {"balance": float(amount)}})
            return True
        except Exception as e:
            print(f"Error inserting income: {e}")
            return False

    def retrieve_incomes(self, user_id):
        try:
            records = self.db.records.find({"$and": [{"user_id": ObjectId(user_id)},{"type": "income"}]}).sort([("date_time", -1), ("_id", -1)])
            records = list(records)

            account_ids = list({record['account_id'] for record in records})
            accounts = self.db.accounts.find({"_id": {"$in": account_ids}})
            account_map = {str(account['_id']): account['account_name'] for account in accounts}

            for record in records:
                if 'date_time' in record:
                    if isinstance(record['date_time'], str):
                        record['formatted_date'] = datetime.fromisoformat(record['date_time']).strftime('%b %d, %Y %H:%M')
                    elif isinstance(record['date_time'], datetime):
                        record['formatted_date'] = record['date_time'].strftime('%b %d, %Y %H:%M')
                
                record['account_name'] = account_map.get(str(record['account_id']), "Deleted Account")
            
            return records

        except Exception as e:
            print(f"Error retrieving records: {e}")
            return []

    def pie_chart_by_category(self, expenses):
        categories = {}
        for record in expenses:
            category = record['record_category']
            categories[category] = categories.get(category, 0) + record['amount']

        fig = Figure(data=[Pie(labels=list(categories.keys()), values=list(categories.values()))])
        pie_chart = pio.to_html(fig, full_html=False)
        return pie_chart

    def bar_chart_by_account(self, expenses):
        accounts = {}
        for record in expenses:
            account_name = record['account_name']
            accounts[account_name] = accounts.get(account_name, 0) + record['amount']

        fig = Figure(data=[Bar(x=list(accounts.keys()), y=list(accounts.values()))])
        fig.update_layout(xaxis_title="Accounts", yaxis_title="Total Amount")
        return pio.to_html(fig, full_html=False)
    
    def insert_transfer(self, user_id, from_account_id, to_account_id, amount, date_time, description):
        try:
            from_account = self.db.accounts.find_one({"_id": from_account_id})
            to_account = self.db.accounts.find_one({"_id": to_account_id})

            if from_account['balance'] < float(amount):
                return False

            self.db.accounts.update_one({"_id": from_account_id}, {"$inc": {"balance": - float(amount)}})
            self.db.accounts.update_one({"_id": to_account_id}, {"$inc": {"balance": float(amount)}})

            self.db.records.insert_one({
                'user_id': ObjectId(user_id),
                'type': 'transfer',
                'from_account_id': from_account_id,
                'to_account_id': to_account_id,
                'amount': float(amount),
                'date_time': date_time,
                'description': description
            })

            return True
        except Exception as e:
            print(f"Error inserting transfer: {e}")
            return False

    def retrieve_transfers(self, user_id):
        try:
            records = self.db.records.find({"$and": [{"user_id": ObjectId(user_id)}, {"type": "transfer"}]}).sort([("date_time", -1), ("_id", -1)])
            records = list(records)

            account_ids = list({record['from_account_id'] for record in records} | {record['to_account_id'] for record in records})
            accounts = self.db.accounts.find({"_id": {"$in": account_ids}})
            account_map = {str(account['_id']): account['account_name'] for account in accounts}

            for record in records:
                record['_id'] = str(record['_id'])
                record['user_id'] = str(record['user_id'])
                record['from_account_id'] = str(record['from_account_id'])
                record['to_account_id'] = str(record['to_account_id'])

                if 'date_time' in record:
                    if isinstance(record['date_time'], str):
                        record['formatted_date'] = datetime.fromisoformat(record['date_time']).strftime('%b %d, %Y %H:%M')
                    elif isinstance(record['date_time'], datetime):
                        record['formatted_date'] = record['date_time'].strftime('%b %d, %Y %H:%M')

                record['from_account_name'] = account_map.get(record['from_account_id'], "Deleted Account")
                record['to_account_name'] = account_map.get(record['to_account_id'], "Deleted Account")
            
            return records
        except Exception as e:
            print(f"Error retrieving transfers: {e}")
            return []
        
    def delete_account(self, user_id, account_id):
        try:
            self.db.accounts.delete_one({"_id": ObjectId(account_id), "user_id": ObjectId(user_id)})
            return True
        except Exception as e:
            print(f"Error deleting account: {e}")
            return False
    
    def delete_record(self, user_id, record_id):
        try:
            self.db.records.delete_one({"_id": ObjectId(record_id), "user_id": ObjectId(user_id)})
            return True
        except Exception as e:
            print(f"Error deleting record: {e}")
            return False