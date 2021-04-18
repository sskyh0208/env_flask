from wtforms.form import Form
from wtforms.fields import StringField, PasswordField, SubmitField, TextAreaField, HiddenField
from wtforms.validators import DataRequired, Email, EqualTo
from wtforms import ValidationError
from flaskr.models import User

# ログイン画面
class LoginForm(Form):
    email = StringField('メールアドレス', render_kw={"placeholder": "メールアドレス"}, validators=[DataRequired(), Email()])
    password = PasswordField('パスワード', render_kw={"placeholder": "パスワード"}, validators=[DataRequired(), EqualTo('confirm_password', message='パスワードが一致しません')])
    confirm_password = PasswordField('パスワード確認', render_kw={"placeholder": "パスワード確認"}, validators=[DataRequired()])
    submit = SubmitField('ログイン')

# 登録画面
class RegisterForm(Form):
    email = StringField('メールアドレス', render_kw={"placeholder": "メールアドレス"}, validators=[DataRequired(), Email()])
    username = StringField('ユーザ名', render_kw={"placeholder": "ユーザ名"}, validators=[DataRequired()])
    submit = SubmitField('登録')

    def validate_email(self, filed):
        if User.select_by_email(filed.data):
            raise ValidationError('メールアドレスは既に登録されています。')

# 登録確認画面
class ResetPasswordForm(Form):
    password = PasswordField('パスワード', render_kw={'placeholder': 'パスワード'}, validators=[DataRequired(), EqualTo('confirm_password', message='パスワードが一致しません')]
    )
    confirm_password = PasswordField('パスワード確認', render_kw={'placeholder': 'パスワード確認'}, validators=[DataRequired()])
    submit = SubmitField('パスワード更新')

    def validate_password(self, field):
        if len(field.data) < 8:
            raise ValidationError('パスワードは8文字以上です')


# 単語登録画面
class WordForm(Form):
    text = StringField('英単語', render_kw={'placeholder': 'do it.'}, validators=[DataRequired()])
    comment = StringField('意味', render_kw={'placeholder': '意味'}, validators=[DataRequired()])
    submit = SubmitField('登録')

# ブック登録画面
class BookForm(Form):
    name = StringField('ブック名', render_kw={'placeholder': 'your book name.'}, validators=[DataRequired()])
    description = StringField('説明', render_kw={'placeholder': '説明'}, validators=[DataRequired()])
    submit = SubmitField('新規作成')