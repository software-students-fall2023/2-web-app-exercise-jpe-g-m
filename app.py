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

#print out the first document in the pets collection
# print(pets.find_one())


@app.route('/')
def index():
    return render_template('edit.html')


@app.route('/edit', methods=['POST'])
def edit_user():
    pet_id = ObjectId(request.form.get('pet_id'))
    new_breed = str(request.form.get('new_breed'))
    
    pets.update_one({"_id": pet_id}, {"$set": {"breed": new_breed}})
    
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)