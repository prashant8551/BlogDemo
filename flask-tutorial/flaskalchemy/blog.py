from flask import Flask,Blueprint, render_template,redirect,request,flash,url_for,abort,g,session
from flaskalchemy.db import Post, db, User
from flaskalchemy.auth import login_required
from sqlalchemy import desc
from . import Mail,Message,mail
bg = Blueprint('blog', __name__,template_folder='template')


@bg.route('/')
def index():
    return redirect(url_for("blog.showblog"))

@bg.route('/add',methods=['GET','POST'])
def add():
    if request.method == 'POST':
        if not request.form['category'] or not request.form['title'] or not request.form['body']:
            flash('Please enter all the fields', 'error')
        else:
            # for i in range(50):
            blog = Post(request.form['category'],request.form['title'],request.form['body'], g.user.id)
            db.session.add(blog)
            db.session.commit()
            # msg = Message(str(blog.title),sender = 'prashantmali.info@gmail.com', recipients = [blog.user.username])  
            # msg.body = str(blog.body)
            # mail.send(msg)    
            print("send",".............")
            return redirect(url_for('blog.index'))
            if True:
                return redirect_back(url_for('blog.showblog'))

    return render_template('blog/create.html')

@bg.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        g.user = User.query.filter_by(id=user_id).first()

    print(g.user,"............name")

@bg.route('/showblog')
def showblog():
    # blog = db.engine.execute(
    #     'SELECT p.id, title, body, pub_date, a_id, username'
    #     ' FROM post p JOIN user u ON p.a_id= u.id'
    #     ' ORDER BY pub_date DESC'
    # ).fetchall()

    # username=User.query.get(user.id)
    # print(username.name,",,,,,,")
    # db.session.query(Post).delete()
    # db.session.commit()
    blog=Post.query.order_by(desc(Post.pub_date)).all()
    c=len(blog)
    return render_template('show_blog.html', blog=blog,user=g.user,c=str(c))


@bg.route('/go',methods=('GET','POST'))
def go():
    if request.method == 'POST':
        id = request.form['pid']
        error = None

        if not id:
            error = 'Title is required.'
            flash(error)
        if error is not None:
            flash(error)
        else:
            post = Post.query.filter_by(id=id).first()
            print("...............",post.id,post.category)
        return render_template('indexpost.html',Post=post)

    

def get_post(id, check_author=True):
    post = Post.query.get(int(id))
    print(post.id)
    print(post.title)
    print(post.body)

    if post is None:
        abort(404, "Post id {0} doesn't exist.".format(id))

    # users_post = User.query.filter(User.id == g.current_user.id).first()

    if check_author and post.a_id != g.user.id:
        abort(403)
    return post


@bg.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_post(int(id))
    print("................post",post.title)
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            post.title=title
            post.body=body
            db.session.add(post)
            db.session.commit()
            # msg = Message(str(post.title),sender = 'prashantmali.info@gmail.com', recipients = [post.user.username])  
            # msg.body = "Updated:"+"Title=>"+str(post.title)+"\n"+"Body=>"+ str(post.body) 
            # mail.send(msg)    
            return redirect(url_for('blog.index'))

    return render_template('blog/update.html', post=post)



@bg.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    db.session.delete(get_post(id))
    db.session.commit()
    return redirect(url_for('blog.showblog'))

@bg.route('/<int:id>/sendemail')
@login_required
def sendemail(id):
    user=User.query.get(int(id))
    posts=Post.query.filter_by(a_id=user.id).first()
    msg = Message(str(posts.title), sender='prashantmali.info@gmail.com', recipients=[user.username])
    msg.body = posts.body
    mail.send(msg)
    return redirect(url_for('blog.index'))

