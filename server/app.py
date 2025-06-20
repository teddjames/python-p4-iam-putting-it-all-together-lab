#!/usr/bin/env python3

from flask import request, session
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from config import app, db, api
from models import User, Recipe

class Signup(Resource):
    def post(self):
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        image_url = data.get('image_url')
        bio = data.get('bio')

        if not username or not password:
            return {'error': 'Username and password are required.'}, 422
    
        user = User(
            username=username,
            image_url=image_url,
            bio=bio
        )
        user.password_hash = password

        db.session.add(user)
        db.session.commit()

        if user:
            session['user_id'] = user.id
            return user.to_dict(), 201
        return {}, 422

class CheckSession(Resource):
    def get(self):
        user = User.query.filter(User.id == session.get('user_id')).first()
        if user:
            return user.to_dict(), 200
        return {'message': '401: Not Authorized'}, 401

    pass

class Login(Resource):
    def post(self):
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        user = User.query.filter_by(username=username).first()

        if user and user.authenticate(password):
            session['user_id'] = user.id
            return user.to_dict(), 201
        return {'message': '401: Not Authorized'}, 401
    

class Logout(Resource):
    def delete(self):
        if session['user_id']:
            session['user_id'] = None
            return {}, 204
        return {}, 401

class RecipeIndex(Resource):
    def get(self):
        user_id = session.get('user_id')
        
        if user_id:
            recipes = Recipe.query.filter(Recipe.user_id == session.get('user_id')).all()
            return [recipe.to_dict() for recipe in recipes], 200
        return {}, 401
    def post(self):
        user_id = session.get('user_id')
        data = request.get_json()
        title = data.get('title')
        instructions = data.get('instructions')
        minutes_to_complete = data.get('minutes_to_complete')

        if not title or not instructions or not minutes_to_complete:
            return {'error': 'Title, instructions and minutes to complete are required'}, 422

        try:
            recipe = Recipe(
                title=title,
                instructions=instructions,
                minutes_to_complete=minutes_to_complete,
                user_id=user_id
            )
            db.session.add(recipe)
            db.session.commit()
            return recipe.to_dict(), 201
        except ValueError as ve:
            return {'error': str(ve)}, 422


        except Exception:
            db.session.rollback()
            return {'error': 'Something went wrong.'}, 500



api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(RecipeIndex, '/recipes', endpoint='recipes')


if __name__ == '__main__':
    app.run(port=5555, debug=True)