from datetime import datetime, timedelta
from uuid import uuid4
from flaskr import db, login_manager
from flask_bcrypt import generate_password_hash, check_password_hash
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), index=True)
    password = db.Column(db.String(128), default=generate_password_hash('default_password'))
    picture_path = db.Column(db.Text)
    description = db.Column(db.String(255))
    is_active = db.Column(db.Boolean, unique=False, default=False)
    create_at = db.Column(db.DateTime, default=datetime.now)
    update_at = db.Column(db.DateTime, default=datetime.now)

    def __init__(self, email, username):
        self.email = email
        self.username = username

    def validate_password(self, password):
        return check_password_hash(self.password, password)
    
    def create_new_user(self):
        db.session.add(self)

    @classmethod
    def select_by_email(cls, email):
        return cls.query.filter_by(email=email).first()

    @classmethod
    def select_user_by_id(cls, id):
        return cls.query.get(id)
    
    @classmethod
    def select_user_by_name(cls, username):
        return cls.query.filter_by(username=username).all()
    
    @classmethod
    def search_description_by_like_word(cls, word):
        return cls.query.filter(cls.description.like(f'%{word}%')).all()

    def save_new_password(self, new_password):
        self.password = generate_password_hash(new_password)
        self.is_active = True

    def update_description(self, value):
        self.description = value

class PasswordResetToken(db.Model):
    __tablename__ = 'password_reset_token'
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(
        db.String(64),
        unique=True,
        index=True,
        default=str(uuid4)
    )
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    expaire_at = db.Column(db.DateTime, default=datetime.now())
    create_at = db.Column(db.DateTime, default=datetime.now())
    update_at = db.Column(db.DateTime, default=datetime.now())

    def __init__(self, token, user_id, expaire_at):
        self.token = token
        self.user_id = user_id
        self.expaire_at = expaire_at

    @classmethod
    def publish_token(cls, user):
        token = str(uuid4())
        new_token = cls(
            token=token,
            user_id=user.id,
            expaire_at=datetime.now() + timedelta(days=1)
        )
        with db.session.begin(subtransactions=True):
            db.session.add(new_token)
        db.session.commit()
        return token
    
    @classmethod
    def get_user_id_by_token(cls, token):
        now = datetime.now()
        record = cls.query.filter_by(token=str(token)).filter(cls.expaire_at > now).first()
        return record.user_id

    @classmethod
    def delete_token(cls, token):
        cls.query.filter_by(token=str(token)).delete()


class Book(db.Model):
    __tablename__ = 'wordbook'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), index=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    description = db.Column(db.String(255))
    typing_mode = db.Column(db.Integer, default=0)
    create_at = db.Column(db.DateTime, default=datetime.now())
    update_at = db.Column(db.DateTime, default=datetime.now())

    def __init__(self, name, user_id, description):
        self.name = name
        self.user_id = user_id
        self.description = description

    @classmethod
    def get_by_id(cls, id):
        return cls.query.get(id)

    @classmethod
    def select_by_user_id(cls, user_id):
        return cls.query.filter_by(user_id=user_id).order_by(cls.create_at.desc()).all()

    def create_new_book(self):
        db.session.add(self)

    @classmethod
    def delete(cls, id):
        cls.query.filter_by(id=id).delete()
        Word.query.filter_by(book_id=id).delete()

    def update(self):
        self.update_at = datetime.now()
        db.session.add(self)

    def change_typing_mode(self, mode_num):
        self.typing_mode = mode_num
        db.session.add(self)


class Word(db.Model):
    __tablename__ = 'words'
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('wordbook.id'), nullable=False)
    text = db.Column(db.Text)
    comment = db.Column(db.String(255))
    create_at = db.Column(db.DateTime, default=datetime.now())
    update_at = db.Column(db.DateTime, default=datetime.now())

    def __init__(self, book_id, text, comment):
        self.book_id = book_id
        self.text = text
        self.comment = comment

    @classmethod
    def get_by_id(cls, id):
        return cls.query.get(id)

    @classmethod
    def get_book_words(cls, book_id):
        return cls.query.filter_by(book_id=book_id).order_by(cls.create_at.desc()).all()

    def create_new_word(self):
        db.session.add(self)

    @classmethod
    def delete(cls, id):
        cls.query.filter_by(id=id).delete()


class Score(db.Model):
    __tablename__ = 'score'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    word_id = db.Column(db.Integer, db.ForeignKey('words.id'), nullable=False)
    typemiss_count = db.Column(db.Integer)
    create_at = db.Column(db.DateTime, default=datetime.now())

    def __init__(self, user_id, word_id, typemiss_count):
        self.user_id = user_id
        self.word_id = word_id
        self.typemiss_count = typemiss_count

    def create_new_score(self):
        db.session.add(self)

    @classmethod
    def get_book_score(cls, book_id):
        return cls.query.filter_by(book_id=book_id).order_by(cls.typemiss_count.desc()).all()

    @classmethod
    def clear_score(cls, user_id):
        cls.query.filter_by(user_id=user_id).delete()