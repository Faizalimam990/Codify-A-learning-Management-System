from sqlalchemy import Column, Integer, String, Boolean, ForeignKey,LargeBinary
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False, unique=True)
    role = Column(String(100))
    progress=Column(String(100),nullable=True)
    password = Column(String(100), nullable=False)
    enrolled_courses = Column(Integer, ForeignKey('courses.id'))
    courses = relationship('Course', backref='user')
    def __str__(self):
        return f"{self.title} - {self.content}"
    

class Course(Base):
    __tablename__ = 'courses'
    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    description = Column(String(500))
    course_thumbnail=Column(LargeBinary,nullable=True)
    lessons = relationship('Lesson', back_populates='course', cascade="all, delete-orphan")

class Lesson(Base):
    __tablename__ = 'lessons'
    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    content = Column(String(200), nullable=False)
    completed = Column(Boolean, default=False)
    course_link = Column(String(500), nullable=False)
    course_id = Column(Integer, ForeignKey('courses.id'))
    course = relationship('Course', back_populates='lessons')
    def __str__(self):
       return f"{self.title} - {self.content}"


class Blogpost(Base):
    __tablename__='blogs'
    id=Column(Integer,primary_key=True)
    title=Column(String(200),nullable=False)
    category=Column(String(200),nullable=True)
    description=Column(String(500),nullable=False)
    thumbnail=Column(String(500),nullable=False)

class Enrollment(Base):
    __tablename__ = 'enrollments'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    course_id = Column(Integer, ForeignKey('courses.id'), nullable=False)
    user = relationship('User', back_populates='enrollments')
    course = relationship('Course', back_populates='enrollments')
    
# Add relationships to the User and Course models
User.enrollments = relationship('Enrollment', back_populates='user')
Course.enrollments = relationship('Enrollment', back_populates='course')










    
# class Quiz(Base):
#     __tablename__ = 'quizzes'
#     id = Column(Integer, primary_key=True)
#     title = Column(String(100), nullable=False)
#     course_id = Column(Integer, ForeignKey('courses.id'))
#     course = relationship('Course', back_populates='quiz')
#     questions = relationship('Question', back_populates='quiz', cascade="all, delete-orphan")


# class Question(Base):
#     __tablename__ = 'questions'
#     id = Column(Integer, primary_key=True)
#     text = Column(String(300), nullable=False)
#     option1 = Column(String(100), nullable=False)
#     option2 = Column(String(100), nullable=False)
#     option3 = Column(String(100), nullable=False)
#     correct_option = Column(String(100), nullable=False)
#     quiz_id = Column(Integer, ForeignKey('quizzes.id'))
#     quiz = relationship('Quiz', back_populates='questions')


# Course.quiz = relationship('Quiz', uselist=False, back_populates='course')