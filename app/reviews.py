from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from auth import check_rights
from models import Review
from app import PER_PAGE, db

review_bp = Blueprint('reviews', __name__, url_prefix='/reviews')

@review_bp.route('/moderate')
@login_required
@check_rights('moderate_review')
def moderate():
    page = request.args.get('page', 1, type=int)

    reviews = Review.query.filter(Review.review_status_id == 1).order_by(Review.created_at.desc())
    pagination = reviews.paginate(page, PER_PAGE)
    reviews = pagination.items

    return render_template('review/reviews.html', reviews=reviews, pagination=pagination)


@review_bp.route('/moderate/<int:review_id>')
@login_required
@check_rights('moderate_review')
def moderate_id(review_id):
    review = Review.query.get(review_id)
    return render_template('review/review.html', review=review)


@review_bp.route('/my_reviews')
@login_required
def my_reviews():
    reviews = Review.query.filter(Review.user_id == current_user.id).all()
    return render_template('review/my_reviews.html', reviews=reviews)

@review_bp.route('/moderate/<int:review_id>/approve')
@login_required
@check_rights('moderate_review')
def approve(review_id):
    review = Review.query.get(review_id)
    review.review_status_id = 2

    try:    
        db.session.add(review)
        db.session.commit()
    except:
        db.session.rollback()
        flash('При модерации рецензии возникла ошибка.', 'warning')
        return redirect(url_for('reviews.moderate'))

    flash('Рецензия успешно одобрена.', 'success')
    return redirect(url_for('reviews.moderate'))

@review_bp.route('/moderate/<int:review_id>/reject')
@login_required
@check_rights('moderate_review')
def reject(review_id):
    review = Review.query.get(review_id)
    review.review_status_id = 3

    try:    
        db.session.add(review)
        db.session.commit()
    except:
        db.session.rollback()
        flash('При модерации рецензии возникла ошибка.', 'warning')
        return redirect(url_for('reviews.moderate'))

    flash('Рецензия успешно отклонена.', 'success')
    return redirect(url_for('reviews.moderate'))