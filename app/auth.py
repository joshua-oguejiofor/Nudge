import secrets

from argon2 import PasswordHasher
from argon2.exceptions import VerificationError, VerifyMismatchError
from flask import flash, redirect, render_template, request, session, url_for
from flask_login import login_required, login_user, logout_user
from sqlalchemy import exists, select

from app.workers.celery_config import celery_app

from .extensions import db
from .model import User

ph = PasswordHasher()


def auth_route(app):
   
    @app.route('/Register', methods=['POST', 'GET'])
    def register():
        if request.method == 'GET':
            return render_template('auth/register.html')
         
        data = request.form
        username = data.get('name',"").strip().lower()
        email = data.get('email',"").strip().lower()
        password = data.get('password',"").strip()
        
        if not username or not email  or not password:
            flash("All fields are required", "danger")
            return redirect(url_for('register'))
        
        db_user = bool(db.session.scalar(
            select(
                exists()
                .where(User.email == email)
                   )))
                   
        if db_user:
            flash("Email already exist.", "warning")
            return redirect(url_for("register"))
            
        hashed_password = ph.hash(password)
        
        user = {
            "username": username,
            "password": hashed_password,
            "email": email
            }
        
        create_acct_code = secrets.token_hex(4).upper()
        session.permanent = True
        session['create_acct_code'] = create_acct_code
        session['user'] = user
                
        celery_app.send_task(
            "send_otp",
            args=[create_acct_code, "Email verification code"]
        )
        return redirect(url_for('verify_code'))      


    @app.route('/verify_code', methods=['POST', 'GET'])
    def verify_code():
        if request.method == 'GET':
            return render_template('auth/code.html')
        
        data = request.form
        
        code = data.get('code',"").strip()
        if not code: 
            flash('Code reqired.', "warning")
            return redirect(url_for("verify_code"))
        
        password_reset_code = session.get('reset_password_code')
        create_acct_code = session.get('create_acct_code')
        
        if code == password_reset_code: 
            session.pop('reset_password_code', None)
            return render_template('auth/update.html')
        
        elif code == create_acct_code:
            
            data = session.get('user')
            
            user = User(**data)
            db.session.add(user)
            db.session.commit()
            
            session.pop('user', None)
            session.pop('create_acct_code', None)
            return redirect(url_for('login'))
            
        else:
            flash('Invalid expire or code', "danger")
            return redirect(url_for("verify_code"))
            
                        
    @app.route('/', methods=['POST', 'GET'])
    def login():
        if request.method == 'GET':
            return render_template('auth/login.html')
        
        data = request.form
        email = data.get('email',"").strip().lower()
        password = data.get('password', "").strip()
        if not email or not password:
            flash('Name and password required', "warning")
            return redirect(url_for("login"))
        
        db_user = db.session.scalar(
            select(User)
            .where(User.email == email)
                )
        try:
            if db_user and ph.verify(db_user.password, password):
                login_user(db_user)
                flash(f"Welcom {db_user.username}!", "success")
                return redirect(url_for('home'))
                        
        except (VerifyMismatchError, VerificationError):
            pass
        
        # Generic error for both incorrect password and non-existent user
        flash("Invalid email or password, try again.", "danger")
        return redirect(url_for("login"))
           
        

    @app.route('/reset_password', methods=['GET','POST'])
    def reset_password():
        if request.method == 'GET':
            return render_template('auth/reset_password.html')
        
        data = request.form
        email = data.get('email',"").lower().strip()
        
        if not email:
            flash('Please add an email', "warning")
            return redirect(url_for("reset_password"))
        
        db_user = db.session.scalar(
            select(User)
            .where(User.email == email)
            )
        if not db_user:
            flash('Invalid email', "danger")
            return redirect(url_for("reset_password"))
        
        password_reset_code = secrets.token_hex(4)
        session.permanent = True
        session['reset_password_code'] = password_reset_code
        session['email'] = email
        
        celery_app.send_task(
            "send_otp",
            args=[password_reset_code, "Password reset code"]
        )
        
        return redirect(url_for('verify_code'))
        

        
    @app.route('/change-password', methods=['POST','GET'])
    def new_details():
        if request.method == 'GET':
            return render_template('auth/update.html')
        
        password = request.form.get('password', '').strip()
        email = session.get('email')
        if not password :
            flash('Please add a password.', "warning")
            return redirect(url_for("new_details"))
                
        db_user = db.session.scalar(
            select(User)
            .where(User.email == email)
            )
        if not db_user:
            flash("Invalid email", "danger")
            return redirect(url_for("new_details"))

        db_user.password = ph.hash(password)
        db.session.commit()
        session.pop('email', None)
        return redirect(url_for('login'))
            

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        flash('Logged successfull.', 'success')
        return redirect(url_for('login'))

