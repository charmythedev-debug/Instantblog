from datetime import datetime
from flask import Flask, abort, render_template, redirect, url_for, flash, request
from flask_bootstrap import Bootstrap5
from flask_ckeditor import CKEditor
from flask_gravatar import Gravatar
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user, login_required
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Text
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash

from forms import *
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
import os



##### todo: touch up: flash messages, user profile pics, refactor html, secret key?,
## todo: brush up on decorators
## todo add profile route that works, have an about me, etc.

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('FLASK_KEY')
ckeditor = CKEditor(app)
Bootstrap5(app)

# TODO: Configure Flask-Login ✅ i think


# CREATE DATABASE
class Base(DeclarativeBase):
    pass
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)

##################### login manager//poster only decorator ########################

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

def post_author_only(f):
    @wraps(f)
    def decorated_function(post_id, *args, **kwargs):
        post = db.get_or_404(BlogPost, post_id)

        is_admin = current_user.is_authenticated and current_user.id == 1
        is_author = current_user.is_authenticated and post.author == current_user.username

        if not (is_admin or is_author):
            return abort(403)

        return f(post_id, *args, **kwargs)
    return decorated_function
@app.context_processor
def inject_current_year():
    return {"current_year": datetime.now().year}




# CONFIGURE TABLES
class BlogPost(db.Model):
    __tablename__ = "blog_posts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    subtitle: Mapped[str] = mapped_column(String(250), nullable=False)
    date: Mapped[str] = mapped_column(String(250), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    author: Mapped[str] = mapped_column(String(250), nullable=False)
    img_url: Mapped[str] = mapped_column(String(250), nullable=False)

    comments = relationship("Comment", backref="post", cascade="all, delete")


# TODO: Create a User table for all your registered users. ✅

class User(UserMixin, db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    password: Mapped[str] = mapped_column(String(100))
    username: Mapped[str] = mapped_column(String(1000), unique=True)

    def __init__(self, email: str, username: str, password: str):
        self.email = email
        self.username = username
        self.password = password


class Comment(db.Model):
    __tablename__ = "comments"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)

    # Foreign keys
    author_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    post_id: Mapped[int] = mapped_column(ForeignKey("blog_posts.id"))

    # Relationships
    author = relationship("User", backref="comments")




with app.app_context():

    db.create_all()

gravatar = Gravatar(app,
                    size=100,
                    rating='g',
                    default='retro')


# TODO: Use Werkzeug to hash the user's password when creating a new user.✅
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():

        existing_user = db.session.execute(db.select(User).filter_by(email=form.email.data)).scalar_one_or_none()
        existing_username = db.session.execute(db.select(User).filter_by(username=form.username.data)).scalar_one_or_none()
        if existing_user:
            flash("Email already registered. Please log in.", "danger")
            return redirect(url_for('login'))
        elif existing_username:
            flash("Username already registered. Try again.", "danger")
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(form.password.data, method='pbkdf2:sha256', salt_length=8)
        new_user = User(email=form.email.data,
                        username=form.username.data,
                        password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)

        return redirect(url_for('get_all_posts'))
    # todo come back to this ✅

    return render_template("register.html", form=form)


# TODO: Retrieve a user from the database based on their email(well we did username). ✅
@app.route('/login', methods = ['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():

        username = form.username.data
        password = form.password.data

        user = db.session.execute(db.select(User).filter_by(username=username)).scalar_one_or_none()
        if user and check_password_hash(user.password, password):

            login_user(user)
            flash('Welcome Back!', 'success')

            return redirect(url_for('get_all_posts'))
        else:
            flash("(╯°□°）╯︵ ┻━┻ Login failed!", "danger")

    return render_template("login.html", form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('get_all_posts'))


@app.route('/')
def get_all_posts():
    result = db.session.execute(db.select(BlogPost))
    posts = result.scalars().all()
    return render_template("index.html", all_posts=posts)


# TODO: Allow logged-in users to comment on posts ✅

@app.route("/post/<int:post_id>", methods=["GET", "POST"])
def show_post(post_id):
    form = CommentForm()
    requested_post = db.get_or_404(BlogPost, post_id)
    comment = None

    if current_user.is_authenticated and form.validate_on_submit():
        comment_text = form.comment.data
        new_comment = Comment(
            text=comment_text,
            author=current_user,
            post=requested_post
        )
        db.session.add(new_comment)
        db.session.commit()
        return redirect(url_for('show_post', post_id=post_id))

    all_comments = requested_post.comments  # via relationship
    return render_template("post.html", post=requested_post, form=form, comments=all_comments)


# TODO: Use a decorator so only an admin user can create a new post(admin and poster) ✅
@app.route("/new-post", methods=["GET", "POST"])
@login_required
def add_new_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        new_post = BlogPost(
            title=form.title.data,
            subtitle=form.subtitle.data,
            body=form.body.data,
            img_url=form.img_url.data,
            author=current_user.username,
            date=datetime.today().strftime("%B %d, %Y")
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("get_all_posts"))
    return render_template("make-post.html", form=form)


# TODO: Use a decorator so only an admin user can edit a post ✅
@app.route("/edit-post/<int:post_id>", methods=["GET", "POST"])
@login_required
@post_author_only
def edit_post(post_id):

    post = db.get_or_404(BlogPost, post_id)
    edit_form = CreatePostForm(
        title=post.title,
        subtitle=post.subtitle,
        img_url=post.img_url,
        author=post.author,
        body=post.body
    )
    if edit_form.validate_on_submit():
        post.title = edit_form.title.data
        post.subtitle = edit_form.subtitle.data
        post.img_url = edit_form.img_url.data
        post.author = current_user.username
        post.body = edit_form.body.data
        db.session.commit()
        return redirect(url_for("show_post", post_id=post.id))
    return render_template("make-post.html", form=edit_form, is_edit=True)


# TODO: Use a decorator so only an admin user can delete a post ✅
@app.route("/delete/<int:post_id>")
@post_author_only
def delete_post(post_id):
    post_to_delete = db.get_or_404(BlogPost, post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('get_all_posts'))


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")

##### profile ###
@app.route("/profile")
@login_required
def profile():
    username = current_user.username

    # Posts authored by the user
    posts = db.session.query(BlogPost).filter_by(author=username).all()

    # Comments written by the user
    comments = db.session.query(Comment).filter_by(author=current_user).all()

    # Posts the user has commented on (distinct)
    commented_on = (
        db.session.query(BlogPost)
        .join(Comment, BlogPost.id == Comment.post_id)
        .filter(Comment.author == current_user)
        .distinct()
        .all()
    )

    return render_template(
        "profile.html",
        username=username,
        posts=posts,
        comments=comments,
        commented_on=commented_on
    )


if __name__ == "__main__":
    app.run(debug=True, port=5002)
