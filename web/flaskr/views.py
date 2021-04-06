from flask import Blueprint, abort, render_template, redirect, url_for ,request, flash
from flask_login import login_user, login_required, logout_user, current_user

from flaskr import db
from flaskr.models import User, PasswordResetToken, Word, Book
from flaskr.forms import LoginForm, RegisterForm, ResetPasswordForm, WordForm, AccountForm, BookForm

bp = Blueprint('app', __name__, url_prefix='')

@bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    return render_template('index.html')

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('app.login'))

@bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        user = User.select_by_email(form.email.data)
        if user and user.is_active and user.validate_password(form.password.data):
            login_user(user, remember=True)
            next = request.args.get('next')
            if not next:
                next = url_for('app.index')
            return redirect(next)
        elif not user:
            flash('存在しないユーザです')
        elif not user.is_active:
            flash('無効なユーザです、パスワードを再設定してください')
        elif not user.validate_password(form.password.data):
            flash('メールアドレス、またはパスワードが間違っています')
    return render_template('login.html', form=form)

@bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    print(request.method)
    if request.method == 'POST' and form.validate():
        user = User(
            email=form.email.data,
            username=form.username.data
        )
        with db.session.begin(subtransactions=True):
            user.create_new_user()
        db.session.commit()
        token = PasswordResetToken.publish_token(user)
        print(f'パスワード設定用URL: http://127.0.0.1:5000/reset_password/{str(token)}')
        return redirect(url_for('app.login'))
    return render_template('register.html', form=form)

@bp.route('/reset_password/<uuid:token>', methods=['GET', 'POST'])
def reset_password(token):
    form = ResetPasswordForm(request.form)
    reset_user_id = PasswordResetToken.get_user_id_by_token(token)

    if not reset_user_id:
        abort(500)
    if request.method == 'POST' and form.validate():
        password = form.password.data
        user = User.select_user_by_id(reset_user_id)
        with db.session.begin(subtransactions=True):
            user.save_new_password(password)
            PasswordResetToken.delete_token(token)
        db.session.commit()
        flash('パスワードを更新しました')
        return redirect(url_for('app.login'))
    return render_template('reset_password.html', form=form)

# ユーザ情報
@bp.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    form = AccountForm(request.form)
    user = User.select_user_by_id(current_user.id)
    if request.method == 'POST' and form.validate():
        with db.session.begin(subtransactions=True):
            user.update_description(form.description.data)
        db.session.commit()
        return redirect(url_for('app.index'))
    return render_template('account.html', user=user, form=form)

# ブック画面
@bp.route('/books', methods=['GET', 'POST'])
@login_required
def books():
    form = BookForm(request.form)
    if request.method == 'POST' and form.validate():
        book = Book(
            name=form.name.data,
            user_id=current_user.id,
            description=form.description.data
        )
        with db.session.begin(subtransactions=True):
            book.create_new_book()
        db.session.commit()
        return redirect(url_for('app.books'))
    books = Book.select_by_user_id(current_user.id)
    return render_template('books.html', form=form, books=books)


@bp.route('/words/<int:book_id>', methods=['GET', 'POST'])
@login_required
def words(book_id):
    form = WordForm(request.form)
    if request.method == 'POST' and form.validate():
        word = Word(
            book_id=book_id,
            text=form.text.data,
            comment=form.comment.data
        )
        with db.session.begin(subtransactions=True):
            word.create_new_word()
        db.session.commit()
        return redirect(url_for('app.words', book_id=book_id))
    words = Word.get_book_words(book_id)
    book = Book.get_by_id(book_id)
    return render_template('words.html', form=form, words=words, book=book)


# # ブックの更新
# @bp.route('/update_book/', methods=['POST'])
# @login_required
# def update():
#     id = request.form.get('id')
#     text = request.form.get('text').strip()
#     comment = request.form.get('comment').strip()
#     word = Word.get_by_id(id)
#     if not word.check(text, comment):
#         with db.session.begin(subtransactions=True):
#             word.update(
#                 text=text,
#                 comment=comment
#             )
#         db.session.commit()
#     return redirect(url_for('app.words'))

# 単語の更新
@bp.route('/update_word', methods=['POST'])
@login_required
def update():
    id = request.form.get('id')
    book_id = request.form.get('book_id')
    text = request.form.get('text').strip()
    comment = request.form.get('comment').strip()
    word = Word.get_by_id(id)
    if not word.check(text, comment):
        with db.session.begin(subtransactions=True):
            word.update(
                text=text,
                comment=comment
            )
        db.session.commit()
    return redirect(url_for('app.words', book_id=book_id))

# ブックの削除
@bp.route('/delete_book/<int:book_id>')
@login_required
def delete_book(book_id):
    with db.session.begin(subtransactions=True):
        Book.delete(book_id)
    db.session.commit()
    return redirect(url_for('app.books'))

# 単語の削除
@bp.route('/delete_word/<int:book_id>/<int:word_id>')
@login_required
def delete_word(book_id, word_id):
    with db.session.begin(subtransactions=True):
        # ブックに紐づいている単語も削除する
        Word.delete(word_id)
    db.session.commit()
    return redirect(url_for('app.words', book_id=book_id))

# ゲーム
@bp.route('/game/<int:book_id>')
@login_required
def game(book_id):
    words = Word.get_book_words(book_id)
    type_words = [{'text': word.text, 'comment': word.comment} for word in words]
    
    return render_template('game.html', words=type_words)