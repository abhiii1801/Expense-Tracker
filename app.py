from flask import Flask, render_template, request, session, redirect, url_for
from user.validation import validation
from datetime import datetime

app = Flask(__name__)
users = validation()
app.secret_key = 'hello123'


@app.route("/")
def redirect_to():
    return redirect("/home")

@app.route("/home/")
def home():
    if session.get('logged_in'):
        return redirect(url_for('analysis'))
    return render_template("login-register-selection.html")

@app.route("/login/", methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        validate = users.login_validation(email, password)

        if validate == 1:
            return render_template('login.html', message='Email does not exist', email=email)
        elif validate == -1:
            return render_template('login.html', message='Incorrect Password', email=email)
        elif validate ==0:
            return render_template('login.html', message='Something went wrong', email=email)
        else:
            session['logged_in'] = True
            session['user_id'] = str(validate)
            print(validate)
            return redirect(url_for('home'))

@app.route("/register/", methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    elif request.method == 'POST':
        fullname = request.form.get('fullname')
        email = request.form.get('email')
        password = request.form.get('password')
        
        insert = users.insert_user(fullname, email, password)

        if insert == True:
            return render_template('register.html', message="Registered Successfully")
        elif insert == 0:
            return render_template('register.html', message="Email already exists",fullname=fullname,email=email)
        else:
            return render_template('register.html', message="Something went wrong",fullname=fullname,email=email)

@app.route("/logout/")
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('home'))

@app.route("/home/analysis/",methods=['GET'])
def analysis():
    if session.get('logged_in'):
        accounts = users.retrieve_accounts(session.get('user_id'))
        expenses = users.retrieve_expenses(session.get('user_id'))
        incomes = users.retrieve_incomes(session.get('user_id'))
        transfers = users.retrieve_transfers(session.get('user_id'))
        pie_expenses = users.pie_chart_by_category(expenses)
        bar_expenses = users.bar_chart_by_account(expenses)
        return render_template("analysis.html", title = "SpendWise" ,accounts=accounts, expenses=expenses, incomes=incomes, transfers=transfers, pie_expenses=pie_expenses, bar_expenses=bar_expenses)
    else:
        return redirect(url_for('login'))

@app.route("/home/records/", methods=['GET'])
def records():
    if session.get('logged_in'):
        accounts = users.retrieve_accounts(session.get('user_id'))
        expenses = users.retrieve_expenses(session.get('user_id'))
        incomes = users.retrieve_incomes(session.get('user_id'))
        transfers = users.retrieve_transfers(session.get('user_id'))
        return render_template("records.html", accounts=accounts, expenses=expenses, incomes=incomes, transfers=transfers)

@app.route("/add_account", methods = ['POST'])
def add_account():
    if session.get('logged_in'):
        account_type = request.form.get('accountType')
        account_balance = request.form.get('currentBalance')
        account_name = request.form.get('accountName')

        insert_acc = users.insert_account(account_name ,account_type, account_balance, session.get('user_id'))
        if insert_acc:
            return redirect(url_for('analysis'))
        else:
            return "Error while Inserting New Account"

@app.route("/add_expense", methods = ['POST'])
def add_expense():
    if session.get('logged_in'):
        account_name = request.form.get('accountName')
        amount = request.form.get('amount')
        record_category = request.form.get('recordCategory')
        date_time_str = request.form.get('datetime')
        record_description = request.form.get('recordDescription')

        accounts = users.retrieve_accounts(session.get('user_id'))
        
        account_dict = {account['account_name']: account['_id'] for account in accounts}

        account_id = account_dict.get(account_name)

        date_time = datetime.strptime(date_time_str, '%Y-%m-%dT%H:%M')

        if account_id:
            insert_record = users.insert_expense(session.get('user_id'), account_id, amount, record_category, date_time, record_description)
            if insert_record:
                return redirect(url_for('analysis'))
            else:
                return "Error while inserting expense record"
        else:
            return "Account name not found"

@app.route("/add_income", methods = ['POST'])
def add_income():
    if session.get('logged_in'):
        account_name = request.form.get('accountName')
        amount = request.form.get('incomeAmount')
        record_category = request.form.get('recordCategory')
        date_time_str = request.form.get('datetime')
        record_description = request.form.get('description')

        accounts = users.retrieve_accounts(session.get('user_id'))
        
        account_dict = {account['account_name']: account['_id'] for account in accounts}

        account_id = account_dict.get(account_name)

        date_time = datetime.strptime(date_time_str, '%Y-%m-%dT%H:%M')

        if account_id:
            insert_record = users.insert_income(session.get('user_id'), account_id, amount, record_category, date_time, record_description)
            if insert_record:
                return redirect(url_for('analysis'))
            else:
                return "Error while inserting expense record"
        else:
            return "Account name not found"

@app.route("/add_transfer", methods = ['POST'])
def add_transfer():
    if session.get('logged_in'):
        from_account_name = request.form.get('fromAccount')
        to_account_name = request.form.get('toAccount')
        transfer_amount = request.form.get('transferAmount')
        date_time_str = request.form.get('datetime')
        transfer_description = request.form.get('description')

        accounts = users.retrieve_accounts(session.get('user_id'))
        
        account_dict = {account['account_name']: account['_id'] for account in accounts}

        from_account_id = account_dict.get(from_account_name)
        to_account_id = account_dict.get(to_account_name)

        date_time = datetime.strptime(date_time_str, '%Y-%m-%dT%H:%M')

        if from_account_id and to_account_id:
            # Call the validation method to insert the transfer record into the DB
            insert_record = users.insert_transfer(session.get('user_id'), from_account_id, to_account_id, transfer_amount, date_time, transfer_description)
            if insert_record:
                return redirect(url_for('analysis'))
            else:
                return "Error while inserting transfer record"
        else:
            return "Account names not found"

@app.route("/delete_account", methods = ['POST'])
def delete_account():
    if session.get('logged_in'):
        account_id = request.form.get('account_id')
        delete_account = users.delete_account(session.get('user_id'), account_id)
        if delete_account:
            return redirect(url_for('records'))
        else:
            return "Error while deleting account"

@app.route("/delete_record", methods = ['POST'])
def delete_record():
    if session.get('logged_in'):
        record_id = request.form.get('record_id')
        delete_record = users.delete_record(session.get('user_id'), record_id)
        if delete_record:
            return redirect(url_for('records'))
        else:
            return "Error while deleting record"

if __name__ == '__main__':
    app.run(debug=True, port=5001)

