from datetime import datetime
from itsdangerous import  TimedJSONWebSignatureSerializer as Serializer
from app import db, login_manager, app
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25),nullable=False, unique=True)
    email = db.Column(db.String(25),nullable=False, unique=True)
    user_role = db.Column(db.String(25),nullable=False)
    password = db.Column(db.String(25),nullable=False)
    image_picture = db.Column(db.String(25), nullable=False, default='default.jpg')
    courses = db.relationship('Course', backref='author',lazy=True)

    def get_reset_token(self, expires_sec = 1800):
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')
    @staticmethod                 
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id =  s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)
    
    
    
    
    def __repr__(self):
        return f"<User id:{self.id}, username:{self.username},email:{self.email},user_role:{self.user_role}>"

class Course(db.Model):
    __tablename__='course'
    id=db.Column(db.Integer, primary_key=True)
    course_name = db.Column(db.String(), nullable=False, unique=True)
    course_code = db.Column(db.String(), nullable=False, unique=True)
    year = db.Column(db.String(), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False,
                            default=datetime.utcnow)
    user_id = db.Column(db.Integer,db.ForeignKey('user.id'), nullable=False)
    questions = db.relationship('Question', backref='courses', lazy=True)
    

    def __repr__(self):
        return f"<Course id:{self.id},course_name:{self.course_name},course_code:{self.course_code},year:{self.year}>"


class Question(db.Model):
    __tablename__='question'
    id = db.Column(db.Integer,primary_key=True)
    chapter = db.Column(db.String(), nullable=False)
    title = db.Column(db.String(), nullable=False)
    content = db.Column(db.Text, nullable=False)
    marks=db.Column(db.String(20),nullable=False)
    image_picture = db.Column(db.String(25), nullable=False, default='default.jpg')
    date_posted = db.Column(db.DateTime, nullable=False,default=datetime.utcnow)
    course_id = db.Column(db.Integer,db.ForeignKey('course.id'), nullable=False)
   

    def __repr__(self):
        return f"<Course id:{self.id},chapter:{self.chapter},title:{self.title},marks:{self.marks}>"
    
# class User(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(25),nullable=False, unique=True)
#     email = db.Column(db.String(25),nullable=False, unique=True)
#     role = db.Column(db.String(25),nullable=False, unique=True)
#     password = db.Column(db.String(25),nullable=False)
#     image_picture = db.Column(db.String(25), nullable=False, default='default.jpg')

class question_paper_banner(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    instituation_name = db.Column(db.String(), nullable=False)
    department = db.Column(db.String(), nullable=False)
    logo = db.Column(db.String(), default='logo.jpg')
        