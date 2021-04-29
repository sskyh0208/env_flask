from flask_testing import TestCase
from flaskr import create_app, db
from flaskr.models import User, PasswordResetToken, Book, Word, Score
from flask import url_for
from flask_login import current_user
import os
import unittest

app = create_app()


class TestConfig:
    TESTING = True
    WTF_CSRF_ENABLED = False
    basedir = os.path.abspath(os.path.dirname(__name__))
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'test.db')


class MyTest(TestCase):
    def create_app(self):
        app.config.from_object('test.TestConfig')
        return app
    
    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_register(self):
        with self.client as client:
            # POST
            self.assertEqual(User.query.count(), 0)
            response = client.post(url_for('app.register'),
                data = {
                    'username': 'test',
                    'email': 'test@mail.com',
                }
            )
            self.assertEqual(User.query.count(), 1)
            self.assertEqual(User.query.all()[-1:][0].username, 'test')
            self.assertEqual(User.query.all()[-1:][0].email, 'test@mail.com')
            self.assert_status(response, 302)
            self.assert_redirects(response, url_for('app.login'))

            # 重複確認
            self.assertEqual(User.query.count(), 1)
            response = client.post(url_for('app.register'),
                data = {
                    'username': 'test',
                    'email': 'test@mail.com',
                }
            )
            self.assertEqual(User.query.count(), 1)

            # GET
            response = client.get(url_for('app.register'))
            self.assert_status(response, 200)

    def test_reset_password(self):
        with self.client as client:
            # 新規登録
            self.assertEqual(PasswordResetToken.query.count(), 0)
            response = client.post(url_for('app.register'),
                data = {
                    'username': 'test',
                    'email': 'test@mail.com',
                }
            )
            user = User.query.all()[-1:][0]
            token = PasswordResetToken.query.all()[-1:][0].token
            self.assertEqual(PasswordResetToken.query.count(), 1)
            # GET
            response = client.get(url_for('app.reset_password', token=token))
            self.assert_status(response, 200)

            # パスワードリセット
            # 8文字以下確認
            response = client.post(url_for('app.reset_password', token=token),
                data = {
                    'password': 'pass',
                    'confirm_password': 'pass',
                }
            )

            response = client.post(url_for('app.reset_password', token=token),
                data = {
                    'password': 'password',
                    'confirm_password': 'password',
                }
            )
            self.assertEqual(PasswordResetToken.query.count(), 0)
            self.assertTrue(user.validate_password('password'))

    def test_login(self):
        with self.client as client:
            # 新規登録
            response = client.post(url_for('app.register'),
                data = {
                    'username': 'test',
                    'email': 'test@mail.com',
                }
            )
            # パスワードリセット
            token = PasswordResetToken.query.all()[-1:][0].token
            response = client.post(url_for('app.reset_password', token=token),
                data = {
                    'password': 'password',
                    'confirm_password': 'password',
                }
            )
            # ログイン(OK)
            self.assertTrue(current_user.is_anonymous)
            response = client.post(url_for('app.login'),
                data = {
                    'email': 'test@mail.com',
                    'password': 'password',
                    'confirm_password': 'password',
                }
            )
            self.assert_status(response, 302)
            self.assertRedirects(response, url_for('app.index'))
            self.assertEqual(current_user.username, 'test')

            response = client.get(url_for('app.index'))
            self.assert_status(response, 200)

    def test_login2(self):
        with self.client as client:
            # 新規登録
            response = client.post(url_for('app.register'),
                data = {
                    'username': 'test',
                    'email': 'test@mail.com',
                }
            )
            # ログイン(not user)
            self.assertTrue(current_user.is_anonymous)
            response = client.post(url_for('app.login'),
                data = {
                    'email': 'test2@mail.com',
                    'password': 'pass',
                    'confirm_password': 'pass',
                }
            )
            self.assert_status(response, 200)
            self.assertTrue(current_user.is_anonymous)

            # ログイン(not active)
            response = client.post(url_for('app.login'),
                data = {
                    'email': 'test@email.com',
                    'password': 'default_password',
                    'confirm_password': 'default_password',
                }
            )
            self.assert_status(response, 200)
            self.assertTrue(current_user.is_anonymous)

            # ログイン(password validate error)
            token = PasswordResetToken.query.all()[-1:][0].token
            response = client.post(url_for('app.reset_password', token=token),
                data = {
                    'password': 'password',
                    'confirm_password': 'password',
                }
            )
            response = client.post(url_for('app.login'),
                data = {
                    'email': 'test@mail.com',
                    'password': 'pass',
                    'confirm_password': 'pass',
                }
            )
            self.assert_status(response, 200)
            self.assertTrue(current_user.is_anonymous)

    def test_logout(self):
        with self.client as client:
            # 新規登録
            response = client.post(url_for('app.register'),
                data = {
                    'username': 'test',
                    'email': 'test@mail.com',
                }
            )
            # パスワードリセット
            token = PasswordResetToken.query.all()[-1:][0].token
            response = client.post(url_for('app.reset_password', token=token),
                data = {
                    'password': 'password',
                    'confirm_password': 'password',
                }
            )
            # ログイン(OK)
            self.assertTrue(current_user.is_anonymous)
            response = client.post(url_for('app.login'),
                data = {
                    'email': 'test@mail.com',
                    'password': 'password',
                    'confirm_password': 'password',
                }
            )
            self.assertEqual(current_user.username, 'test')
            # ログアウト
            response = client.get(url_for('app.logout'))
            self.assertTrue(current_user.is_anonymous)

    def test_books(self):
        with self.client as client:
            # 新規登録
            response = client.post(url_for('app.register'),
                data = {
                    'username': 'test',
                    'email': 'test@mail.com',
                }
            )
            # パスワードリセット
            token = PasswordResetToken.query.all()[-1:][0].token
            response = client.post(url_for('app.reset_password', token=token),
                data = {
                    'password': 'password',
                    'confirm_password': 'password',
                }
            )
            # ログイン(OK)
            response = client.post(url_for('app.login'),
                data = {
                    'email': 'test@mail.com',
                    'password': 'password',
                    'confirm_password': 'password',
                }
            )
            self.assertEqual(Book.query.count(), 0)
            response = client.post(url_for('app.books'),
                data = {
                    'name': 'test',
                    'description': 'test',
                }
            )
            self.assertEqual(Book.query.count(), 1)
            self.assert_status(response, 302)
            self.assert_redirects(response, url_for('app.books'))
            self.assertEqual(Book.query.all()[-1:][0].name, 'test')

            response = client.get(url_for('app.books'))
            self.assert_status(response, 200)

    def test_words(self):
        with self.client as client:
            # 新規登録
            response = client.post(url_for('app.register'),
                data = {
                    'username': 'test',
                    'email': 'test@mail.com',
                }
            )
            # パスワードリセット
            token = PasswordResetToken.query.all()[-1:][0].token
            response = client.post(url_for('app.reset_password', token=token),
                data = {
                    'password': 'password',
                    'confirm_password': 'password',
                }
            )
            # ログイン(OK)
            response = client.post(url_for('app.login'),
                data = {
                    'email': 'test@mail.com',
                    'password': 'password',
                    'confirm_password': 'password',
                }
            )
            # ブック作成
            response = client.post(url_for('app.books'),
                data = {
                    'name': 'test',
                    'description': 'test',
                }
            )
            # 単語作成
            self.assertEqual(Word.query.count(), 0)
            response = client.post(url_for('app.words', book_id=1),
                data = {
                    'text': 'test',
                    'comment': 'test',
                }
            )
            self.assertEqual(Word.query.count(), 1)
            self.assert_status(response, 302)
            self.assert_redirects(response, url_for('app.words', book_id=1))
            self.assertEqual(Word.query.all()[-1:][0].text, 'test')

            response = client.get(url_for('app.words', book_id=1))
            self.assert_status(response, 200)

    def test_delete_book(self):
        with self.client as client:
            # 新規登録
            response = client.post(url_for('app.register'),
                data = {
                    'username': 'test',
                    'email': 'test@mail.com',
                }
            )
            # パスワードリセット
            token = PasswordResetToken.query.all()[-1:][0].token
            response = client.post(url_for('app.reset_password', token=token),
                data = {
                    'password': 'password',
                    'confirm_password': 'password',
                }
            )
            # ログイン(OK)
            response = client.post(url_for('app.login'),
                data = {
                    'email': 'test@mail.com',
                    'password': 'password',
                    'confirm_password': 'password',
                }
            )
            # ブック作成
            response = client.post(url_for('app.books'),
                data = {
                    'name': 'test',
                    'description': 'test',
                }
            )
            # ブック削除
            self.assertEqual(Book.query.count(), 1)
            response = client.get(url_for('app.delete_book', book_id=1))
            self.assertEqual(Book.query.count(), 0)
            self.assert_redirects(response, url_for('app.books'))

    def test_delete_words(self):
        with self.client as client:
            # 新規登録
            response = client.post(url_for('app.register'),
                data = {
                    'username': 'test',
                    'email': 'test@mail.com',
                }
            )
            # パスワードリセット
            token = PasswordResetToken.query.all()[-1:][0].token
            response = client.post(url_for('app.reset_password', token=token),
                data = {
                    'password': 'password',
                    'confirm_password': 'password',
                }
            )
            # ログイン(OK)
            response = client.post(url_for('app.login'),
                data = {
                    'email': 'test@mail.com',
                    'password': 'password',
                    'confirm_password': 'password',
                }
            )
            # ブック作成
            response = client.post(url_for('app.books'),
                data = {
                    'name': 'test',
                    'description': 'test',
                }
            )
            # 単語作成
            response = client.post(url_for('app.words', book_id=1),
                data = {
                    'text': 'test',
                    'comment': 'test',
                }
            )
            # 単語削除
            self.assertEqual(Word.query.count(), 1)
            response = client.get(url_for('app.delete_word', book_id=1, word_id=1))
            self.assertEqual(Word.query.count(), 0)
            self.assert_redirects(response, url_for('app.words', book_id=1))

    def test_game(self):
        with self.client as client:
            # 新規登録
            response = client.post(url_for('app.register'),
                data = {
                    'username': 'test',
                    'email': 'test@mail.com',
                }
            )
            # パスワードリセット
            token = PasswordResetToken.query.all()[-1:][0].token
            response = client.post(url_for('app.reset_password', token=token),
                data = {
                    'password': 'password',
                    'confirm_password': 'password',
                }
            )
            # ログイン(OK)
            response = client.post(url_for('app.login'),
                data = {
                    'email': 'test@mail.com',
                    'password': 'password',
                    'confirm_password': 'password',
                }
            )
            # ブック作成
            response = client.post(url_for('app.books'),
                data = {
                    'name': 'test',
                    'description': 'test',
                }
            )
            # 単語作成
            response = client.post(url_for('app.words', book_id=1),
                data = {
                    'text': 'test',
                    'comment': 'test',
                }
            )
            # ゲーム開始
            response = client.get(url_for('app.game', book_id=1))

    def test_score(self):
        with self.client as client:
            # 新規登録
            response = client.post(url_for('app.register'),
                data = {
                    'username': 'test',
                    'email': 'test@mail.com',
                }
            )
            # パスワードリセット
            token = PasswordResetToken.query.all()[-1:][0].token
            response = client.post(url_for('app.reset_password', token=token),
                data = {
                    'password': 'password',
                    'confirm_password': 'password',
                }
            )
            # ログイン(OK)
            response = client.post(url_for('app.login'),
                data = {
                    'email': 'test@mail.com',
                    'password': 'password',
                    'confirm_password': 'password',
                }
            )
            # ブック作成
            response = client.post(url_for('app.books'),
                data = {
                    'name': 'test',
                    'description': 'test',
                }
            )
            # 単語作成
            response = client.post(url_for('app.words', book_id=1),
                data = {
                    'text': 'test',
                    'comment': 'test',
                }
            )
            # スコア
            response = client.get(url_for('app.score', book_id=1))

    def test_game_score(self):
        with self.client as client:
        # 新規登録
            response = client.post(url_for('app.register'),
                data = {
                    'username': 'test',
                    'email': 'test@mail.com',
                }
            )
            # パスワードリセット
            token = PasswordResetToken.query.all()[-1:][0].token
            response = client.post(url_for('app.reset_password', token=token),
                data = {
                    'password': 'password',
                    'confirm_password': 'password',
                }
            )
            # ログイン(OK)
            response = client.post(url_for('app.login'),
                data = {
                    'email': 'test@mail.com',
                    'password': 'password',
                    'confirm_password': 'password',
                }
            )
            # ブック作成
            response = client.post(url_for('app.books'),
                data = {
                    'name': 'test',
                    'description': 'test',
                }
            )
            # 単語作成
            response = client.post(url_for('app.words', book_id=1),
                data = {
                    'text': 'test',
                    'comment': 'test',
                }
            )
            # スコア登録
            self.assertEqual(Score.query.count(), 0)
            response = client.post(url_for('app.game_score'),
                json = [{
                    'book_id': 1,
                    'word_id': 1,
                    'count': 1
                }]
            )
            self.assertEqual(Score.query.count(), 1)
            self.assertEqual(Score.query.all()[-1:][0].typemiss_count, 1)
            self.assertTrue(Score.get_book_score(1))

            # スコア削除

    def test_game_score2(self):
        with self.client as client:
        # 新規登録
            response = client.post(url_for('app.register'),
                data = {
                    'username': 'test',
                    'email': 'test@mail.com',
                }
            )
            # パスワードリセット
            token = PasswordResetToken.query.all()[-1:][0].token
            response = client.post(url_for('app.reset_password', token=token),
                data = {
                    'password': 'password',
                    'confirm_password': 'password',
                }
            )
            # ログイン(OK)
            response = client.post(url_for('app.login'),
                data = {
                    'email': 'test@mail.com',
                    'password': 'password',
                    'confirm_password': 'password',
                }
            )
            # ブック作成
            response = client.post(url_for('app.books'),
                data = {
                    'name': 'test',
                    'description': 'test',
                }
            )
            # 単語作成
            response = client.post(url_for('app.words', book_id=1),
                data = {
                    'text': 'test',
                    'comment': 'test',
                }
            )
            response = client.post(url_for('app.words', book_id=1),
                data = {
                    'text': 'test2',
                    'comment': 'test2',
                }
            )
            # スコア登録
            self.assertEqual(Score.query.count(), 0)
            response = client.post(url_for('app.game_score'),
                json = [
                    {
                        'book_id': 1,
                        'word_id': 1,
                        'count': 1
                    },
                    {
                        'book_id': 1,
                        'word_id': 2,
                        'count': 1
                    }
                ]
            )
            self.assertEqual(Score.query.count(), 2)
            self.assertEqual(Score.query.all()[-1:][0].typemiss_count, 1)
            self.assertEqual(Score.query.all()[-2:][0].typemiss_count, 1)

    def test_change_mode(self):
        with self.client as client:
            # 新規登録
            response = client.post(url_for('app.register'),
                data = {
                    'username': 'test',
                    'email': 'test@mail.com',
                }
            )
            # パスワードリセット
            token = PasswordResetToken.query.all()[-1:][0].token
            response = client.post(url_for('app.reset_password', token=token),
                data = {
                    'password': 'password',
                    'confirm_password': 'password',
                }
            )
            # ログイン(OK)
            response = client.post(url_for('app.login'),
                data = {
                    'email': 'test@mail.com',
                    'password': 'password',
                    'confirm_password': 'password',
                }
            )
            # ブック作成
            response = client.post(url_for('app.books'),
                data = {
                    'name': 'test',
                    'description': 'test',
                }
            )
            # 単語作成
            response = client.post(url_for('app.words', book_id=1),
                data = {
                    'text': 'test',
                    'comment': 'test',
                }
            )

            self.assertEqual(Book.query.all()[-1:][0].typing_mode, 0)
            response = client.post(url_for('app.change_mode'),
                json = {
                    'book_id': 1,
                    'typing_mode': 1
                }
            )
            self.assertEqual(Book.query.all()[-1:][0].typing_mode, 1)



if __name__ == '__main__':
    unittest.main()