from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
from bson import ObjectId
from dotenv import load_dotenv
import os


load_dotenv()

app = Flask(__name__)

# Connect to MongoDB
# Connect to MongoDB Atlas
client = MongoClient(os.environ.get('MONGO_URI'))
db = client[os.environ.get('MONGO_DBNAME')]  
pets = db["pets"]
humans = db["humans"]


#print out the first document in the pets collection
# print(pets.find_one())


@app.route('/')
def index():
    docs = humans.find({})
    return render_template('index.html', docs=docs)




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

if __name__ == '__main__':
    PORT = os.getenv('PORT', 5000)
    app.run(debug=True, port=PORT) 
