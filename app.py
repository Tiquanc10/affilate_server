from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow 
from flask_cors import CORS
from datetime import datetime, timedelta
from flask_bcrypt import Bcrypt
import os

# Init app
app = Flask(__name__)

# Database
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
    os.path.join(basedir, 'app.sqlite')
db = SQLAlchemy(app)
ma = Marshmallow(app)

# Middleware
bcrypt = Bcrypt(app)
cors = CORS(app, resources={r"/*": {"origins": "*"}})

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100), unique=False)

    def __init__(self, email, password):
        self.email = email
        self.password = password
        
class UserSchema(ma.Schema):
    class Meta:
        fields = ('id', 'email', 'password')

user_schema = UserSchema()


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), unique=False)
    desc = db.Column(db.String(200), unique=False)
    category = db.Column(db.String(200), unique=False)
    url = db.Column(db.String(5000), unique=False)
    img_url =db.Column(db.String(5000), unique=False)

    def __init__(self, title, desc, category, url, img_url):
        self.title = title
        self.desc = desc
        self.category = category
        self.url = url
        self.img_url = img_url


class PostSchema(ma.Schema):
    class Meta: 
        fields = ('id', 'title', 'desc', 'category', 'url', 'img_url')


post_schema = PostSchema()
posts_schema = PostSchema(many=True)

# Endpoint to Add a User
@app.route('/user', methods=['POST'])
def add_user():
    email = request.json['email']
    password = request.json['password']

    user_check = db.session.query(User).filter(User.email == email).first()

    if user_check is not None:
        return jsonify('Please choose a different email')

    new_user = User(email, password)

    db.session.add(new_user)
    db.session.commit()

    result = user_schema.dump(new_user)

    return jsonify({'user': result})

# Endpoint to login user
@app.route('/login', methods=['POST'])
def login_user():
    email = request.json['email']
    password = request.json['password']

    user = db.session.query(User).filter(User.email == email).first()

    if user == None:
        return jsonify('User does not exist')
    
    if user.password != password:
        return jsonify('Wrong password')

    return jsonify({'LOGGED_IN': True})

# Endpoint to Create a New post
@app.route('/post', methods=['POST'])
def add_post():
    title = request.json['title']
    desc = request.json['desc']
    category = request.json['category']
    url = request.json['url']
    img_url = request.json['img_url']
    new_post = Post(title, desc, category, url, img_url)

    db.session.add(new_post)
    db.session.commit()

    post = Post.query.get(new_post.id)
    return post_schema.jsonify(post)

# Endpoint to query all posts
@app.route('/posts', methods=['GET'])
def get_posts():
    all_posts = Post.query.all()
    result = posts_schema.dump(all_posts)
    return jsonify(result)

# Endpoint to query one post
@app.route('/post/<id>', methods=['GET'])
def get_post(id):
    post = Post.query.get(id)
    return post_schema.jsonify(post)

# Endpoint to update a post
@app.route('/post/<id>', methods=['PUT'])
def update_post(id):
    post = Post.query.get(id)
    title = request.json['title']
    desc = request.json['desc']
    category = request.json['category']
    url = request.json['url']
    img_url = request.json['img_url']
    new_post = Post(title, desc, category, url, img_url)

    post.title = title
    post.desc = description
    post.category = category
    post.url = url
    post.img_url = img_url

    db.session.commit()
    return post_schema.jsonify(post)

# Endpoint to delete a post
@app.route('/post/<id>', methods=['DELETE'])
def delete_post(id):
    post = Post.query.get(int(id))
    db.session.delete(post)
    db.session.commit()

    return 'Post was successfully deleted!'


if __name__ == '__main__':
    app.run(debug=True)
