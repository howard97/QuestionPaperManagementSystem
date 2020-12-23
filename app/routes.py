from app import app,db,bcrypt, mail
from flask import render_template, url_for,request, flash, redirect
from app.models import User, Course, Question
from app.form import RegistrationForm, LoginForm, CourseForm, QuestionForm, RequestResetForm, ResetPasswordForm
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/register', methods=['GET','POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('welcome'))
    form = RegistrationForm()
    if form.validate_on_submit():
        try:
            hashed_password = bcrypt.generate_password_hash(
                form.password.data).decode('utf-8')
            user = User(username=form.username.data,
                        email=form.email.data,user_role=form.user_role.data, password=hashed_password)
            db.session.add(user)
            db.session.commit()
            flash('Your account has been created, You are now able to Log In', 'success')
            return redirect(url_for('login'))
        except:
            db.session.rollback()
        finally:
            db.session.close()
            
    return render_template('register.html', title='Register', form=form)
   


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('welcome'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('Login unsuccessful, Please check your Email and Password', 'danger')
    return render_template('login.html', form=form)



@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))
    


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/quetion/create', methods=['GET','POST'])
@login_required
def create_question():
    form = QuestionForm()
    if form.validate_on_submit():
        try:
            course = Course.query.filter_by(user_id=current_user.id).first()
            question=Question(chapter=form.chapter.data, title=form.title.data, content=form.content.data, marks=form.marks.data, course_id=course.id)
            db.session.add(question)
            db.session.commit()
            flash('The Question has been created seccessfuly.','success')
            return redirect(url_for('welcome'))
        except:
            db.session.rollback()
        finally:
            db.session.close()
    return render_template('question.html', form=form)

@app.route('/find_question')
@login_required
def find_question():
    course = Course.query.filter_by(user_id=current_user.id).first()
    questions= Question.query.filter_by(course_id=course.id)
    return render_template('find_question.html', questions=questions, course=course)

@app.route('/edit', methods=['GET', 'POST'])
def edit():
    if request.method == 'POST':
        question = Question.query.get(request.form.get('id'))
        question.content = request.form['content']
        question.marks = request.form['marks']
        db.session.commit()
        flash('question updated successfully', 'success')
        return redirect(url_for('find_question'))
    

@app.route('/create/question', methods=['GET','POST'])
def question_create():
    error = False
    try:
        chapter = request.form.get('chapter')
        title = request.form.get('title')
        content = request.form.get('content')
        marks = request.form.get('marks')
        course = Course.query.filter_by(user_id=current_user.id).first()
        question=Question(chapter=chapter, title=title, content=content, marks=marks, course_id=course.id)
        db.session.add(question)
        db.session.commit()
        flash('Question created successfully','success')
    except:
        error = True
        db.session.rollback()
    finally:
        db.session.close()
    if not error:
        return redirect(url_for('find_question'))


@app.route('/course/create', methods=['GET','POST'])
@login_required
def create_course():
    form = CourseForm()
    if form.validate_on_submit():
        try:
            course = Course(course_name=form.course_name.data, course_code=form.course_code.data, year = form.class_year.data, user_id=current_user.id)
            db.session.add(course)
            db.session.commit()
            flash(f'{form.course_name.data} has been created seccessfuly.','success')
            return redirect(url_for('find_course'))
        except:
            db.session.rollback 
        finally:
            db.session.close()
            
    return render_template('course.html', form=form)

@app.route('/delete/<id>', methods=['GET', 'POST'])
def delete(id):
    question = Question.query.get(id)
    db.session.delete(question)
    db.session.commit()
    flash('Question deleted successfully')

    return redirect(url_for('find_question'))

@app.route('/find_course')
@login_required
def find_course():
    courses = Course.query.filter_by(user_id=current_user.id)
    return render_template('find_course.html', courses=courses)


@app.route('/welcome')
@login_required
def welcome():
    return render_template('welcome.html')


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request', sender='howard12.sakala@gmail.com', recipients=[user.email])
    msg.body=f''' To reset your password, Visit the following link:
    {url_for('reset_token', token=token, _external=True)}
        
    If you did not make this request, simply ignore this email and no changes will be made
    '''
    mail.send(msg)


@app.route('/reset_password', methods=['GET','POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('welcome'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email = form.email.data).first()
        send_reset_email(user)
        flash('An Email has been sent with instructions to reset Your Password.', 'info')
        return redirect(url_for('login'))
    return render_template('reset_request.html', title = 'Reset Password', form=form)



@app.route('/reset_password/<token>', methods=['GET','POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('welcome'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is invalid or expired token', 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        try:
            hashed_password = bcrypt.generate_password_hash(
                form.password.data).decode('utf-8')
            user.password=hashed_password
            db.session.commit()
            flash('Your Your Password has been updated, You are now able to Log In', 'success')
            return redirect(url_for('login'))
        except:
            db.session.rollback()
        finally:
            db.session.close()
            
    return render_template('reset_token.html', title = 'Reset Password', form=form)
