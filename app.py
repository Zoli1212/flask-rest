import os
from flask import Flask, request
from flask_restful import Api, Resource
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = os.environ.get('SQLALCHEMY_TRACK_MODIFICATIONS')
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY')
print('SQLALCHEMY_DATABASE_URI:', app.config['SQLALCHEMY_DATABASE_URI'])
print('SQLALCHEMY_TRACK_MODIFICATIONS:', app.config['SQLALCHEMY_TRACK_MODIFICATIONS'])
print('JWT_SECRET_KEY:', app.config['JWT_SECRET_KEY'])
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://student:student@localhost:3306/my_flask'

db = SQLAlchemy(app)
api = Api(app)
jwt = JWTManager(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

    def __init__(self, username, password):
        self.username = username
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

class TodoItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.String(255), nullable=False)
    done = db.Column(db.Boolean, default=False)

class TodoList(Resource):
    @jwt_required()
    def get(self):
        current_user = get_jwt_identity()
        items = TodoItem.query.filter_by(user_id=current_user['id']).all()
        return {'items': [{'id': item.id, 'content': item.content, 'done': item.done} for item in items]}

    @jwt_required()
    def post(self):
        current_user = get_jwt_identity()
        content = request.json.get('content')
        item = TodoItem(user_id=current_user['id'], content=content)
        db.session.add(item)
        db.session.commit()
        return {'id': item.id, 'content': item.content, 'done': item.done}

class TodoItemResource(Resource):
    @jwt_required()
    def put(self, id):
        current_user = get_jwt_identity()
        item = TodoItem.query.filter_by(id=id, user_id=current_user['id']).first()
        item.done = True
        db.session.commit()
        return {'id': item.id, 'content': item.content, 'done': item.done}

    @jwt_required()
    def delete(self, id):
        current_user = get_jwt_identity()
        item = TodoItem.query.filter_by(id=id, user_id=current_user['id']).first()
        db.session.delete(item)
        db.session.commit()
        return {'id': item.id, 'content': item.content, 'done': item.done}

class AuthRegister(Resource):
    def post(self):
        username = request.json.get('username')
        password = request.json.get('password')
        if not username or not password:
            return {'message': 'Missing username or password'}, 400
        if User.query.filter_by(username=username).first():
            return {'message': 'Username already taken'}, 400
        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()
        return {'message': 'User created successfully'}, 201

class AuthLogin(Resource):
    def post(self):
        username = request.json.get('username')
        password = request.json.get('password')
        if not username or not password:
            return {'message': 'Missing username or password'}, 400
        user = User.query.filter_by(username=username).first()
        if not user or not user.check_password(password):
            return {'message': 'Invalid credentials'}, 401
        access_token = create_access_token({'id': user.id, 'username': user.username})
        return {'access_token': access_token}
    
class HelloWorld(Resource):
    def get(self):
        return {'message': 'Hello, world!'}

api.add_resource(TodoList, '/todo')
api.add_resource(TodoItemResource, '/todo/int:id')
api.add_resource(AuthRegister, '/register')
api.add_resource(AuthLogin, '/login')
api.add_resource(HelloWorld, '/')

if __name__ == '__main__':
    db.create_all()
    app.run(host='0.0.0.0',debug=True)
