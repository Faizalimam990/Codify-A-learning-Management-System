from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Float, DateTime, LargeBinary
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func

Base = declarative_base()

# User Model
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False, unique=True)
    role = Column(String(100))
    password = Column(String(100), nullable=False)
    progress = relationship('UserProgress', back_populates='user', cascade="all, delete-orphan")
    enrollments = relationship('Enrollment', back_populates='user', cascade="all, delete-orphan")
    answers = relationship('UserAnswer', back_populates='user', cascade="all, delete-orphan")

# Course Model
class Course(Base):
    __tablename__ = 'courses'
    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    description = Column(String(500))
    course_thumbnail = Column(LargeBinary, nullable=True)
    lessons = relationship('Lesson', back_populates='course', cascade="all, delete-orphan")
    quizzes = relationship('Quiz', back_populates='course', cascade="all, delete-orphan")
    progress = relationship('UserProgress', back_populates='course', cascade="all, delete-orphan")
    enrollments = relationship('Enrollment', back_populates='course', cascade="all, delete-orphan")

# Lesson Model
class Lesson(Base):
    __tablename__ = 'lessons'
    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    content = Column(String(200), nullable=False)
    completed = Column(Boolean, default=False)
    course_link = Column(String(500), nullable=False)
    course_id = Column(Integer, ForeignKey('courses.id', ondelete='CASCADE'))
    course = relationship('Course', back_populates='lessons')

# Blogpost Model
class Blogpost(Base):
    __tablename__ = 'blogs'
    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    category = Column(String(200), nullable=True)
    description = Column(String(500), nullable=False)
    thumbnail = Column(String(500), nullable=False)

# Enrollment Model
class Enrollment(Base):
    __tablename__ = 'enrollments'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    course_id = Column(Integer, ForeignKey('courses.id', ondelete='CASCADE'), nullable=False)
    user = relationship('User', back_populates='enrollments')
    course = relationship('Course', back_populates='enrollments')

# Quiz Model

class Quiz(Base):
    __tablename__ = 'quizzes'
    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    course_id = Column(Integer, ForeignKey('courses.id', ondelete='CASCADE'), nullable=False)
    course = relationship('Course', back_populates='quizzes')
    questions = relationship('Question', back_populates='quiz', cascade="all, delete-orphan")
    user_progress = relationship('UserProgress', back_populates='quiz', cascade="all, delete-orphan")


class Question(Base):
    __tablename__ = 'questions'
    id = Column(Integer, primary_key=True)
    question_text = Column(String(255), nullable=False)
    option_1 = Column(String(100), nullable=False)
    option_2 = Column(String(100), nullable=False)
    option_3 = Column(String(100), nullable=False)
    option_4 = Column(String(100), nullable=False)
    correct_option = Column(Integer, nullable=False)
    quiz_id = Column(Integer, ForeignKey('quizzes.id', ondelete='CASCADE'), nullable=False)
    quiz = relationship('Quiz', back_populates='questions')
    user_answers = relationship('UserAnswer', back_populates='question', cascade="all, delete-orphan")  # Add this line

# UserProgress Model
class UserProgress(Base):
    __tablename__ = 'user_progress'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    course_id = Column(Integer, ForeignKey('courses.id', ondelete='CASCADE'), nullable=False)
    quiz_id = Column(Integer, ForeignKey('quizzes.id', ondelete='CASCADE'), nullable=True)  # Foreign key added
    lessons_completed = Column(Integer, default=0)
    quiz_score = Column(Float, default=0.0)
    last_updated = Column(DateTime, server_default=func.now(), onupdate=func.now())
    questions_answered = Column(Integer)

    user = relationship('User', back_populates='progress')
    course = relationship('Course', back_populates='progress')
    quiz = relationship('Quiz')  # The relationship now works


class UserAnswer(Base):
    __tablename__ = 'user_answers'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    question_id = Column(Integer, ForeignKey('questions.id', ondelete='CASCADE'), nullable=False)
    selected_option = Column(Integer, nullable=False)
    is_correct = Column(Integer, default=0)  # 0 for incorrect, 1 for correct

    user = relationship('User', back_populates='answers')
    question = relationship('Question', back_populates='user_answers')