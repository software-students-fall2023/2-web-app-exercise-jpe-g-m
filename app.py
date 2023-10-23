from flask import Flask, flash, render_template, request, redirect, url_for, session
from pymongo import MongoClient
from bson import ObjectId
from dotenv import load_dotenv
import os


load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Connect to MongoDB
# Connect to MongoDB Atlas

#default connection string
client = MongoClient ('mongodb+srv://admi:sSq4KE8jp6DgusOD@cluster0.35ye0fk.mongodb.net')
db = client ['SWE']

#client = MongoClient(os.getenv('MONGO_URI'), serverSelectionTimeoutMS=5000)
#db = client[os.getenv('MONGO_DBNAME')]  


pets = db["pets"]
humans = db["humans"]
shelters = db["shelters"]

pets.create_index([
    ("breed", "text"),
    ("type", "text")
])

#print out the first document in the pets collection
# print(pets.find_one())
user_id = None



@app.route('/')
def landing():
    return render_template('landing.html')

@app.route('/index')
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



@app.route('/index_shelter')
def index_shelter():
    user_id = session.get('user_id')
    if not user_id:
        # Not logged in, redirect to login page
        return redirect(url_for('login'))

    user_doc = shelters.find_one({"_id": ObjectId(user_id)})
    if not user_doc:
        # User not found, clear the session and redirect to login
        session.clear()
        return redirect(url_for('login'))
    return render_template('index_shelter.html', user_doc=user_doc)



@app.route('/edit/<user_id>')
def edit(user_id):
    doc = humans.find_one({"_id": ObjectId(user_id)})
    if doc:
        return render_template('edit.html', doc=doc)


@app.route('/edit/<user_id>', methods=['POST'])
def edit_user(user_id):
    # Get the new values from the form
    username = request.form.get('username')
    passw = request.form.get('passw')

    # Prepare the update data
    update_data = {}
    if username:
        update_data["username"] = username
    if passw:
        update_data["passw"] = passw

    # Check if the user is in the humans collection
    if humans.find_one({"_id": ObjectId(user_id)}):
        humans.update_one({"_id": ObjectId(user_id)}, {"$set": update_data})
        return redirect(url_for('index'))

    





@app.route('/edit_shelter/<user_id>')
def edit_shelter(user_id):
    doc = shelters.find_one({"_id": ObjectId(user_id)})
    if doc:
        return render_template('edit_shelter.html', doc=doc)


@app.route('/edit_shelter/<user_id>', methods=['POST'])
def edit_shelterDone(user_id):
    # Get the new values from the form
    username = request.form.get('username')
    passw = request.form.get('passw')

    # Prepare the update data
    update_data = {}
    if username:
        update_data["username"] = username
    if passw:
        update_data["passw"] = passw

    # Check if the user is in the shelters collection
    if shelters.find_one({"_id": ObjectId(user_id)}):
        shelters.update_one({"_id": ObjectId(user_id)}, {"$set": update_data})
        return redirect(url_for('index_shelter'))
    



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        passw = request.form.get('passw')

        # Check credentials for humans
        user = humans.find_one({"username": username, "passw": passw})
        shelter = shelters.find_one({"username": username, "passw": passw})
        
        if user:
            # Credentials are correct for a human
            session['user_id'] = str(ObjectId(user['_id']))
            return redirect(url_for('index'))

        # Check credentials for shelters
      
        if shelter:
            # Credentials are correct for a shelter
            session['user_id'] = str(ObjectId(shelter['_id']))
            return redirect(url_for('index_shelter'))

        # Invalid credentials
        return render_template('login.html', error="Invalid username or password")
    
    return render_template('login.html')



@app.route('/search', methods=['GET', 'POST'])
def search():
    user_id = session.get('user_id')
    user_doc = humans.find_one({"_id": ObjectId(user_id)})
    liked_pets = user_doc['likedPets']
    
    results = []
    if request.method == 'POST':
        query = request.form.get('query')
        results = pets.find({"$text": {"$search": query}, "_id": {"$nin": liked_pets}})
    return render_template('search.html', results=results,)
    



@app.route('/add', methods=['GET','POST'])
def add():
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        address = request.form.get('address')
        username = request.form.get('username')
        passw = request.form.get('passw')

        user = humans.find_one({"username": username, "passw": passw})
        print("user::: ",user)

        if (user):
            # User Already exists
            return redirect('login.html', error="User already exists, please login")
        else:
            # Create New User
            humans.insert_one({
                "first_name": first_name,
                "last_name": last_name,
                "address": address,
                "username": username,
                "passw": passw,
                "likedPets": []
                })
            user = humans.find_one({"username": username, "passw": passw})

            session['user_id'] = str(ObjectId(user['_id']))
            return redirect(url_for('index'))
    return render_template('add.html')



@app.route('/add_shelter', methods=['GET','POST'])
def add_shelter():
    if request.method == 'POST':
        company = request.form.get('company')
        location = request.form.get('location')
        username = request.form.get('username')
        passw = request.form.get('passw')

        user = shelters.find_one({"username": username, "passw": passw})
        print("user::: ",user)

        if (user):
            # User Already exists
            return redirect('login.html', error="User already exists, please login")
        else:
            # Create New Shelter
            shelters.insert_one({
                "company": company,
                "location": location,
                "username": username,
                "passw": passw,
                "Pets": []
                })
            user = shelters.find_one({"username": username, "passw": passw})

            session['user_id'] = str(ObjectId(user['_id']))
            return redirect(url_for('index_shelter'))
    return render_template('add_shelter.html')







@app.route('/delete_account')
def delete_account():
    user_id = session.get('user_id')
    if not user_id:
        # Not logged in, redirect to login page
        return redirect(url_for('login'))

    # Render a confirmation page before actual deletion
    return render_template('delete_account.html')

@app.route('/confirm_delete', methods=['POST'])
def confirm_delete():
    user_id = session.get('user_id')
    if not user_id:
        # Not logged in, redirect to login page
        return redirect(url_for('login'))

    try:
        # Actually delete the user's data from the database
        if humans.find_one({"_id": ObjectId(user_id)}):
            humans.delete_one({"_id": ObjectId(user_id)})

        elif shelters.find_one({"_id": ObjectId(user_id)}):
            shelters.delete_one({"_id": ObjectId(user_id)})

        # Clear the user session and other data
        session.pop('user_id', None)
        # if you stored anything else in session, clear it here

        flash('Your account has been deleted.', 'success')
        return redirect(url_for('landing'))  # or wherever you want to redirect after deletion

    except Exception as e:
        # Log the error for debugging
        print(str(e))
        flash('There was a problem deleting your account.', 'error')
        return redirect(url_for('delete_account'))




@app.route('/like/<pet_id>')
def like_pet(pet_id):
    user_id = session.get('user_id')
    humans.update_one({"_id": ObjectId(user_id)}, {"$addToSet": {"likedPets": ObjectId(pet_id)}})
    return redirect(url_for('search'))

@app.route('/liked', methods=['GET'])
def liked_pets():
    user_id = session.get('user_id')
    user_doc = humans.find_one({"_id": ObjectId(user_id)})
    liked_pets_ids = user_doc['likedPets']
    liked_pets_list = pets.find({"_id": {"$in": liked_pets_ids}})
    return render_template('liked_pets.html', liked_pets=liked_pets_list)




@app.route('/add_pets', methods=['GET','POST'])
def add_pets():
    if request.method == 'POST':
        name = request.form.get('name')
        age = request.form.get('age')
        breed = request.form.get('breed')
        type = request.form.get('type')

        # Create New pet
        pets.insert_one({
                "name": name,
                "age": age,
                "breed": breed,
                "type": type,
                })
        return redirect(url_for('index_shelter'))
    return render_template('add_pets.html')


@app.route('/added_pets', methods=['GET'])
def added_pets():
    user_id = session.get('user_id')
    user_doc = shelters.find_one({"_id": ObjectId(user_id)})
    pets_ids = user_doc['Pets']
    current_pets_list = pets.find({"_id": {"$in": pets_ids}})
    return render_template('pets_list.html', pets_list=current_pets_list)


if __name__ == '__main__':
    PORT = os.getenv('PORT', 5000)
    app.run(debug=True, port=PORT) 
