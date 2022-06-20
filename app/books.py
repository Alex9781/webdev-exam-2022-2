import bleach

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required

from app import db
from models import Book, Review, Genre
from auth import check_rights
from tools import ImageSaver

book_bp = Blueprint('books', __name__, url_prefix='/books')


@book_bp.route('/<int:book_id>')
def show(book_id):
    book = Book.query.get(book_id)
    return render_template('book/show.html', book=book)


@book_bp.route('/create', methods=['GET', 'POST'])
@login_required
@check_rights('create_book')
def create():
    genres = Genre.query.all()
    genres_count = len(genres)

    if request.method == 'POST':
        try:
            book = Book()
            book.title = bleach.clean(request.form.get('book_title'))
            book.short_description = bleach.clean(
                request.form.get('book_short_description'))
            book.author = bleach.clean(request.form.get('book_author'))
            book.publisher = bleach.clean(request.form.get('book_publisher'))
            book.publish_year = request.form.get('book_publish_year')
            book.volume = request.form.get('book_volume')

            for genre_id in request.form.getlist('book_genres'):
                genre = Genre.query.get(genre_id)
                book.genres.append(genre)

            db.session.add(book)

            f = request.files.get('book_img')
            if f and f.filename:
                ImageSaver(f, book).save()

            flash('Книга успешно добавлена.', 'success')
            return redirect(url_for('index'))
        except:
            db.session.rollback()
            flash(
                'При сохранении данных возникла ошибка. Проверьте корректность введённых данных.', 'warning')
            return render_template(
                'book/create.html',
                genres=genres,
                genres_count=genres_count,
                book=book,
                book_genres=book.genres)
        finally:
            db.session.commit()

    return render_template('book/create.html', genres=genres, genres_count=genres_count, book=None)


@book_bp.route('/<int:book_id>/delete', methods=['POST'])
@login_required
@check_rights('delete_book')
def delete(book_id):
    book = Book.query.get(book_id)
    db.session.delete(book)
    db.session.commit()

    flash('Книга успешно удалена.', 'success')
    return redirect(url_for('index'))
