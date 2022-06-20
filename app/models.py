import sqlalchemy
import os

from flask_login import UserMixin
from flask import url_for
from werkzeug.security import check_password_hash
from markdown import markdown

from app import db, app
from user_policy import UsersPolicy


class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(100), nullable=False, unique=True)
    password_hash = db.Column(db.String(256), nullable=False)

    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    middle_name = db.Column(db.String(100))

    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)
    role = db.relationship('Role')

    def check_password(self, password: str):
        return check_password_hash(self.password_hash, password)

    @property
    def full_name(self):
        return ' '.join([self.last_name, self.first_name, self.middle_name or ''])

    @property
    def is_admin(self):
        return app.config.get('ADMIN_ROLE_ID') == self.role_id

    @property
    def is_moderator(self):
        return app.config.get('MODERATOR_ROLE_ID') == self.role_id

    @property
    def is_user(self):
        return app.config.get('USER_ROLE_ID') == self.role_id

    def can(self, action, book_id=None):
        user_policy = UsersPolicy(book_id)
        method = getattr(user_policy, action)
        if method is not None: return method()
        else: return False


class Role(db.Model):
    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.String(100), nullable=False)


books_genres = db.Table('books_genres',
    db.Column('id', db.Integer, primary_key=True),
    db.Column('book_id', db.Integer, db.ForeignKey('books.id'), nullable=False),
    db.Column('genre_id', db.Integer, db.ForeignKey('genres.id'), nullable=False)
)


class Book(db.Model):
    __tablename__ = 'books'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False, unique=True)

    short_description = db.Column(db.Text, nullable=False)

    author = db.Column(db.String(100), nullable=False)

    publisher = db.Column(db.String(100), nullable=False)
    publish_year = db.Column(db.DateTime, nullable=False)

    volume = db.Column(db.Integer, nullable=False)

    genres = db.relationship('Genre', secondary=books_genres, cascade="all, delete")
    image = db.relationship('BookImage', cascade="all, delete, delete-orphan")
    reviews = db.relationship('Review', cascade="all, delete, delete-orphan")

    @property
    def score(self):
        sum = 0
        for review in self.reviews:
            sum += review.rating

        try:
            return sum / len(self.reviews)
        except ZeroDivisionError:
            return 0

    @property
    def reviews_count(self):
        return len(self.reviews)

    @property
    def formatted_description(self):
        return markdown(self.short_description)

class Genre(db.Model):
    __tablename__ = 'genres'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)


class BookImage(db.Model):
    __tablename__ = 'books_images'

    id = db.Column(db.String(100), primary_key=True)

    file_name = db.Column(db.String(100), nullable=False)
    mime_type = db.Column(db.String(100), nullable=False)

    md5_hash = db.Column(db.String(100), nullable=False, unique=True)

    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    book = db.relationship('Book')

    @property
    def storage_filename(self):
        _, ext = os.path.splitext(self.file_name)
        return self.id + ext

    @property
    def url(self):
        return url_for('image', image_id=self.id)


class Review(db.Model):
    __tablename__ = 'reviews'

    id = db.Column(db.Integer, primary_key=True)
    rating = db.Column(db.Integer, nullable=False)
    text = db.Column(db.Text, nullable=False)
    
    created_at = db.Column(db.DateTime, nullable=False, server_default=sqlalchemy.sql.func.now())

    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    review_status_id = db.Column(db.Integer, db.ForeignKey('reviews_status.id'), nullable=False, default=1)

    book = db.relationship('Book')
    user = db.relationship('User')
    review_status = db.relationship('ReviewStatus')

    @property
    def formatted_text(self):
        return markdown(self.text)

    @property
    def allowed(self):
        return self.review_status_id == 2

class ReviewStatus(db.Model):
    __tablename__ = 'reviews_status'

    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(100), nullable=False, unique=True)