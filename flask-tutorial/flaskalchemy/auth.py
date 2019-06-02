from random import *  
from flask import Blueprint,request, flash, url_for, redirect, render_template,g,current_app,session
from flaskalchemy.db import User, db,Post
from werkzeug.security import check_password_hash,generate_password_hash
from . import Mail,Message,mail
from sqlalchemy import desc
import functools
# from urllib.parse import urljoin,urlparse
# from flask import request, url_for

# def is_safe_url(target):
#     ref_url = urlparse(request.host_url)
#     test_url = urlparse(urljoin(request.host_url, target))
#     return test_url.scheme in ('http', 'https') and \
#            ref_url.netloc == test_url.netloc

# def get_redirect_target():
#     for target in request.values.get('next'), request.referrer:
#         if not target:
#             continue
#         if is_safe_url(target):
#             return target
# def redirect_back(endpoint, **values):
#     target = request.form['next']
#     if not target or not is_safe_url(target):
#         target = url_for(endpoint, **values)
#     return redirect(url_for('auth.index'))


abp = Blueprint('auth', __name__, template_folder='template')
otp = randint(000000,999999)  


@abp.route('/<int:id>/remove_self')
def remove_self(id):
    User.query.filter(User.id ==int(id)).delete()
    db.session.query(Post).filter(Post.a_id == id).delete()
    db.session.commit()
    # posts = Post.query.filter_by(a_id=author.id).all()
    # db.session.delete(author)
    # db.session.delete(posts)
    return redirect(url_for('auth.login'))


# @abp.route('/changepassword')
# def changepassword():
#     return render_template('changepassword.html')


# @abp.route('/validate_email', methods=['GET', 'POST'])
# def validate_email():
#     if request.method == "POST":
#         error=None
#         user_name=request.form['username']
#         user=User.query.filter_by(username=user_name).first()
#         return redirect(url_for('auth.otploginemail',username=user.username))
#     return render_template('changepassword.html')

# @abp.route('/<username>/verify')
# def otploginemail(username):
#     if request.method=="POST":
#         print(username,"......................")
#         email = username  
#         msg = Message('OTP',sender = 'prashantmali.info@gmail.com', recipients = [email])  
#         msg.body = str(otp)  
#         l=mail.send(msg)    
#     return render_template('loginotpemail.html',username=username)

# @abp.route('/<user_name>/validate_password',methods=["POST"])  
# def validate_password(user_name):  
#     user_otp = request.form['otp']  
#     if otp == int(user_otp):  
#         return redirect(url_for('auth.resetview',username=user_name))
#     return "<h3>failure</h3>" 

# open a connection to a URL using urllib

import webbrowser

a_website = "https://accounts.google.com/ServiceLogin/identifier?service=mail&passive=true&rm=false&continue=https%3A%2F%2Fmail.google.com%2Fmail%2F&ss=1&scc=1&ltmpl=default&ltmplcache=2&emr=1&osid=1&flowName=GlifWebSignIn&flowEntry=AddSession"

# Open url in a new window of the default browser, if possible

@abp.route('/change_password', methods=['GET', 'POST'])
def validateusername():
    if request.method == "POST":
        error=None
        user_name=request.form['username']
        user=User.query.filter_by(username=user_name).first()
        msg = Message('changepassword link',sender = 'prashantmali.info@gmail.com', recipients = [user.username])  
        msg.body = f"http://localhost:5000/{user.username}/resetview" 
        mail.send(msg) 
        webbrowser.open_new(a_website)
    return render_template('changepassword.html')

@abp.route('/<username>/resetview', methods=['GET', 'POST'])
def resetview(username):
    if request.method == "POST":
        error=None
        new_password = request.form['newpassword']
        c_password = request.form['confirmpassword']

        if new_password == c_password:
            user=User.query.filter_by(username=username).first()
            user.password=generate_password_hash(new_password)
            db.session.add(user)
            db.session.commit()
            msg = Message('Password_Change',sender = 'prashantmali.info@gmail.com', recipients = [user.username])  
            msg.body = f'username:{user.username} and new_password:{new_password}' 
            mail.send(msg)    
            print("send",".............")
            return redirect(url_for('auth.login'))
        else:
            error="Password and confirm password not match"
            flash(error)
    return render_template("resetpassword.html")

@abp.route('/show')
def show():
    users = User.query.all()
    l=[]
    s={}
    for user in users:
        d={}
        posts=Post.query.filter_by(a_id=user.id).all()
        #print(user.username,"=>",len(posts))
        d[user.username]=len(posts)
        for key,value in d.items():
            print("key=>",key,"values=>",value)
        l.append(d)
    s["users"]=l
    print(l)
    # for d in l:
    #     print(d)
    #print(s["users"][0][])

    #     for post in posts:
    #         print(post)
    # # db.session.query(User).delete()
    # db.session.commit()
    return render_template('show_user.html', users=users,parent_dict=l)

@abp.route('/<int:id>/deleteuser')
def deleteuser(id):
    User.query.filter(User.id ==int(id)).delete()
    db.session.query(Post).filter(Post.a_id == id).delete()
    db.session.commit()
    # posts = Post.query.filter_by(a_id=author.id).all()
    # db.session.delete(author)
    # db.session.delete(posts)
    return redirect(url_for('auth.show'))

@abp.route('/<username>/verify')
def otplogin(username):
    email = username  
    msg = Message('OTP',sender = 'prashantmali.info@gmail.com', recipients = [email])  
    msg.body = str(otp)  
    mail.send(msg)    
    return render_template('loginotp.html')

@abp.route('/validate',methods=["POST"])  
def validate():  
    user_otp = request.form['otp']  
    if otp == int(user_otp):  
        return redirect(url_for('blog.showblog')) 
    else:    
        return "<h3>failure</h3>" 

@abp.route('/pagination')
def pagination():
    blog = Post.query.order_by(desc(Post.pub_date)).all()
    print(len(blog),"...........")
    return render_template('pagination.html', blog=blog)


@abp.route('/register/', methods=['GET', 'POST'])
def register():
    if request.method == "POST":
        error=None
        username = request.form['username']
        password = request.form['password']
        c_password=request.form['confirm_password']

        if password == c_password:
            user=User.query.filter_by(username=username).first()
            if not user:
                register = User(username=username, password=password)
                db.session.add(register)
                db.session.commit()
                if False:
                    msg = Message('OTP',sender = 'prashantmali.info@gmail.com', recipients = [register.username])  
                    msg.body = f'username:{register.username} and password:{password}' 
                    mail.send(msg)    
                    print("send",".............")
            else:
                error="Username already exist"
                flash(error)
                # error=""
                # flash(error)
            return redirect(url_for("auth.login"))
            # if True:
            #     return redirect_back(url_for('blog.showblog'))
        else:
            error="Password and confirm password not match"
            flash(error)
    return render_template("auth/add.html")

    


@abp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        error = None
        uname = request.form["username"]
        passw = request.form["password"]

        user = User.query.filter_by(username=uname).first()
        if user and check_password_hash(user.password,passw):
            session.clear()
            session['user_id'] = user.id
            return redirect(url_for('blog.showblog'))
            # if user.username=='admin':
            #     return redirect(url_for('blog.showblog'))
            # elif False:   
            #     return redirect(url_for('auth.otplogin',username=user.username))
        else:
            error = "Please enter valid credential"
            flash(error)
    return render_template("auth/login.html")

@abp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        g.user = User.query.filter_by(id=user_id).first()

# @abp.after_request
# def after_request(response):
#     response.headers.add('Cache-Control', 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0')
#     return response

@abp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('blog.showblog'))


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)
    return wrapped_view
