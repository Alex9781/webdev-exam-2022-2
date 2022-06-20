from flask_login import current_user


class UsersPolicy:
    def __init__(self, book=None):
        self.book = book

    def create_book(self):
        is_create_user = current_user.is_admin
        return is_create_user

    def read_book(self):
        is_reading_user = current_user.is_authenticated
        return is_reading_user

    def update_book(self):
        is_updating_user = current_user.is_admin or current_user.is_moderator
        return is_updating_user

    def delete_book(self):
        is_deleting_user = current_user.is_admin
        return is_deleting_user

    def moderate_review(self):
        is_moderating_review_user = current_user.is_admin or current_user.is_moderator
        return is_moderating_review_user

    def review(self):
        from models import Review
        
        is_reviewing_user = Review.query.filter(
            Review.book_id == self.book.id).filter(
                Review.user_id == current_user.id).first() is None and current_user.is_authenticated
        return is_reviewing_user
