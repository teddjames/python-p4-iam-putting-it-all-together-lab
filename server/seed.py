#!/usr/bin/env python3

from random import randint, choice as rc
from faker import Faker

from app import app
from models import db, User, Recipe

fake = Faker()

with app.app_context():

    print("Deleting all records...")
    Recipe.query.delete()
    User.query.delete()

    print("Creating users...")
    users = []
    usernames = set()

    for _ in range(20):
        username = fake.first_name()
        while username in usernames:
            username = fake.first_name()
        usernames.add(username)

        user = User(
            username=username,
            bio=fake.paragraph(nb_sentences=3),
            image_url=fake.url()
        )
        user.password_hash = username + 'password'

        users.append(user)

    db.session.add_all(users)
    db.session.commit()

    print("Creating recipes...")
    recipes = []
    for _ in range(100):
        instructions = fake.text(max_nb_chars=300)
        while len(instructions) < 50:
            instructions += ' ' + fake.sentence()

        recipe = Recipe(
            title=fake.sentence(),
            instructions=instructions,
            minutes_to_complete=randint(15, 90),
            user_id=rc(users).id
        )

        recipes.append(recipe)

    db.session.add_all(recipes)
    db.session.commit()

    print("Seeding complete.")
