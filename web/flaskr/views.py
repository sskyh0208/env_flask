from flask import Blueprint, abort, render_template, redirect, url_for ,request, flash, jsonify
from flask_login import login_user, login_required, logout_user, current_user

from flaskr import db
from flaskr.models import User, PasswordResetToken, Word, Book, Score
from flaskr.forms import LoginForm, RegisterForm, ResetPasswordForm, WordForm, BookForm
from sqlalchemy import desc

bp = Blueprint('app', __name__, url_prefix='')

@bp.route('/', methods=['GET', 'POST'])
def index():
    login_form = LoginForm()
    register_form = RegisterForm()
    return render_template('index.html', login_form=login_form, register_form=register_form)

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('app.index'))

@bp.route('/login', methods=['POST'])
def login():
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        user = User.select_by_email(form.email.data)
        if user and user.is_active and user.validate_password(form.password.data):
            login_user(user, remember=True)
            next = request.args.get('next')
            if not next:
                next = url_for('app.index')
            return jsonify({'success': True}), 200, {'ContentType': 'application/json'}
            # return redirect(next)
        elif not user:
            return jsonify({'success': False, 'message': '存在しないユーザです'}), 200, {'ContentType': 'application/json'}
        elif not user.is_active:
            return jsonify({'success': False, 'message': '無効なユーザです、パスワードを再設定してください'}), 200, {'ContentType': 'application/json'}
        elif not user.validate_password(form.password.data):
            return jsonify({'success': False, 'message': 'メールアドレス、またはパスワードが間違っています'}), 200, {'ContentType': 'application/json'}
    return jsonify({'success': False, 'message': 'パスワードが間違っています。'}), 200, {'ContentType': 'application/json'}

@bp.route('/register', methods=['POST'])
def register():
    form = RegisterForm(request.form)
    if form.validate():
        user = User(
            email=form.email.data,
            username=form.username.data
        )
        with db.session.begin(subtransactions=True):
            user.create_new_user()
        db.session.commit()
        token = PasswordResetToken.publish_token(user)
        print(f'パスワード設定用URL: http://127.0.0.1:5000/reset_password/{str(token)}')
        return 'メールアドレスにメッセージが送信されました'
    return 'メールアドレスは既に登録されています。'

@bp.route('/reset_password/<uuid:token>', methods=['GET', 'POST'])
def reset_password(token):
    login_form = LoginForm()
    register_form = RegisterForm()
    reset_password_form = ResetPasswordForm(request.form)
    reset_user_id = PasswordResetToken.get_user_id_by_token(token)

    if not reset_user_id:
        abort(500)
    if request.method == 'POST' and reset_password_form.validate():
        password = reset_password_form.password.data
        user = User.select_user_by_id(reset_user_id)
        with db.session.begin(subtransactions=True):
            user.save_new_password(password)
            PasswordResetToken.delete_token(token)
        db.session.commit()
        flash('パスワードを更新しました')
        return redirect(url_for('app.index'))
    return render_template('reset_password.html', login_form=login_form, register_form=register_form, reset_password_form=reset_password_form)

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

# 単語追加画面
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
        book = Book.get_by_id(book_id)
        with db.session.begin(subtransactions=True):
            word.create_new_word()
            book.update()
        db.session.commit()
        return redirect(url_for('app.words', book_id=book_id))
    words = Word.get_book_words(book_id)
    book = Book.get_by_id(book_id)
    return render_template('words.html', form=form, words=words, book=book, words_count=len(words))

# ブックの削除
@bp.route('/delete_book/<int:book_id>')
@login_required
def delete_book(book_id):
    with db.session.begin(subtransactions=True):
        Book.delete(book_id)
        Score.delete_book_scores(current_user.id, book_id)
    db.session.commit()
    return redirect(url_for('app.books'))

# スコアの削除
@bp.route('/delete_score/<int:book_id>')
@login_required
def delete_score(book_id):
    with db.session.begin(subtransactions=True):
        Score.delete_book_scores(current_user.id, book_id)
    db.session.commit()
    return redirect(url_for('app.score', book_id=book_id))

# 単語の削除
@bp.route('/delete_word/<int:book_id>/<int:word_id>')
@login_required
def delete_word(book_id, word_id):
    with db.session.begin(subtransactions=True):
        Word.delete(word_id)
        Score.delete_word_scores(current_user.id, word_id)
    db.session.commit()
    return redirect(url_for('app.words', book_id=book_id))

# ゲーム
@bp.route('/game/<int:book_id>')
@login_required
def game(book_id):
    # タイピングモード切替のためにbook情報呼び出し
    book = Book.get_by_id(book_id)
    words = Word.get_book_words(book_id)
    # javascriptで処理するタイピングワードを作成する。
    type_words = [{'id': word.id, 'text': word.text, 'comment': word.comment, 'book_id': word.book_id} for word in words]
    return render_template('game.html', words=type_words, mode=book.typing_mode, book_name=book.name)


@bp.route('/game/score', methods=['POST'])
@login_required
def game_score():
    scores = [{'user_id': current_user.id, 'book_id': val.get('book_id'), 'word_id': val.get('word_id'), 'typemiss_count': val.get('count')} for val in request.json if val.get('count')]
    if scores:
        if len(scores) == 1:
            score = Score(
                user_id=scores[0].get('user_id'),
                book_id=scores[0].get('book_id'),
                word_id=scores[0].get('word_id'),
                typemiss_count=scores[0].get('typemiss_count')
            )
            with db.session.begin(subtransactions=True):
                score.create_new_score()
            db.session.commit()
        else:
            with db.session.begin(subtransactions=True):
                Score.create_new_scores(scores)
            db.session.commit()

    return jsonify({'result': 'success'})

@bp.route('/score/<int:book_id>')
@login_required
def score(book_id):
    scores = (
        db.session.query(Word, db.func.sum(Score.typemiss_count).label('typemiss_count'))
        .filter(book_id == Word.book_id)
        .filter(Score.word_id == Word.id)
        .filter(Score.user_id == current_user.id)
        .group_by(Word.id)
        .order_by(desc('typemiss_count'))
        .all()
    )
    book = Book.get_by_id(book_id)

    return render_template('score.html', scores=scores, book=book)

@bp.route('/change_mode', methods=['POST'])
@login_required
def change_mode():
    book = Book.get_by_id(request.json.get('book_id'))
    with db.session.begin(subtransactions=True):
        book.change_typing_mode(int(request.json.get('typing_mode')))
    db.session.commit()
    return redirect(url_for('app.books'))