from flask import Flask, render_template, request, redirect, url_for, session
from pymongo import MongoClient
from bson import ObjectId
from dotenv import load_dotenv
import os


load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Connect to MongoDB
# Connect to MongoDB Atlas
client = MongoClient(os.environ.get('MONGO_URI'))
db = client[os.environ.get('MONGO_DBNAME')]  

pets = db["pets"]
humans = db["humans"]

pets.create_index([
    ("breed", "text"),
    ("color", "text")
])

#print out the first document in the pets collection
# print(pets.find_one())


@app.route('/')
def index():
    user_id = session.get('user_id')
    if not user_id:
        # Not logged in, redirect to login page
        return redirect(url_for('login'))

    user_doc = humans.find_one({"_id": ObjectId(user_id)})
    if not user_doc:
        # User not found, clear the session and redirect to login
        session.clear()
        return redirect(url_for('login'))
    return render_template('index.html', user_doc=user_doc)




@app.route('/edit/<user_id>')
def edit(user_id):
    doc = humans.find_one({"_id": ObjectId(user_id)})
    return render_template('edit.html', doc=doc) # render the edit template

@app.route('/edit/<user_id>', methods=['POST'])
def edit_user(user_id):
    # username = ObjectId(request.form.get('username'))
    passw = request.form.get('passw')
    
    humans.update_one({"_id": ObjectId(user_id)}, {"$set": {"passw": passw}})
    
    return redirect(url_for('index'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        passw = request.form.get('passw')

        # Check credentials
        user = humans.find_one({"username": username, "passw": passw})
        if user:
            # Credentials are correct
            session['user_id'] = str(user['_id'])
            return redirect(url_for('index'))
        else:
            # Invalid credentials
            return render_template('login.html', error="Invalid username or password")
    return render_template('login.html')


@app.route('/search', methods=['GET', 'POST'])
def search():
    results = []
    if request.method == 'POST':
        query = request.form.get('query')
        results = pets.find({"$text": {"$search": query}})
    return render_template('search.html', results=results)


@app.route('/add', methods=['POST'])
def add():

    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    address = request.form.get('address')
    username = request.form.get('username')
    passw = request.form.get('passw')

    user = humans.find_one({"username": username, "passw": passw})

    if (user):
        # User Already exists
        return render_template('login.html', error="User already exists, please login")
    else:
        # Create New User
        humans.insert({
            "first_name": first_name,
            "last_name": last_name,
            "address": address,
            "username": username,
            "passw": passw
            })
        return redirect(url_for('index'))
    return redirect('add.html')



if __name__ == '__main__':
    PORT = os.getenv('PORT', 5000)
    app.run(debug=True, port=PORT) 
