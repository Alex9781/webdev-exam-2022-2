import os
import bleach

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy import true

from app import db, app
from models import Book, Review, Genre, BookImage
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

            db.session.commit()

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
                book=book)

    return render_template(
        'book/create.html',
        genres=genres,
        genres_count=genres_count,
        book=None)


@book_bp.route('/<int:book_id>/edit', methods=['GET', 'POST'])
def edit(book_id):
    genres = Genre.query.all()
    genres_count = len(genres)

    book = Book.query.get(book_id)

    if request.method == 'POST':
        try:
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

            db.session.commit()

            flash('Книга успешно обновлена.', 'success')
            return redirect(url_for('index'))
        except:
            db.session.rollback()
            flash(
                'При сохранении данных возникла ошибка. Проверьте корректность введённых данных.', 'warning')
            return render_template(
                'book/edit.html',
                genres=genres,
                genres_count=genres_count,
                book=book,
                publish_year=book.publish_year.strftime('%Y-%m-%d'))

    return render_template(
        'book/edit.html',
        genres=genres,
        genres_count=genres_count,
        book=book,
        publish_year=book.publish_year.strftime('%Y-%m-%d'))


@book_bp.route('/<int:book_id>/delete', methods=['POST'])
@login_required
@check_rights('delete_book')
def delete(book_id):
    try:
        book = Book.query.get(book_id)
        image = BookImage.query.filter(Book.id == book.id).first()

        path_to_img = os.path.join(
            app.config['UPLOAD_FOLDER'], image.storage_filename)

        book.genres.clear()
        db.session.delete(book)
        db.session.commit()

        os.remove(path_to_img)
    except:
        flash('Ошибка при удалении книги.', 'warning')
        return redirect(url_for('index'))

    flash('Книга успешно удалена.', 'success')
    return redirect(url_for('index'))


@book_bp.route('/<int:book_id>/create_review', methods=['POST'])
@login_required
@check_rights('review_book')
def create_review(book_id):
    try:
        review = Review()
        review.rating = request.form.get('review-rating')
        review.text = bleach.clean(request.form.get('review-text'))
        review.book_id = book_id
        review.user_id = current_user.id

        db.session.add(review)
        db.session.commit()

        flash('Рецензия отправлена на проверку.', 'success')
        return redirect(url_for('books.show', book_id=book_id))
    except:
        db.session.rollback()
        flash('При создании рецензии возникла ошибка. Проверьте корректность введённых данных.', 'warning')
        return redirect(url_for('books.show', book_id=book_id))
    
