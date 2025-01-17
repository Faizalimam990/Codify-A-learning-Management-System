from flask import Flask, request, render_template, redirect, url_for, session,flash
from flask_restful import Resource, Api
from werkzeug.security import generate_password_hash, check_password_hash
from models import User, Course,Lesson,Blogpost,Enrollment,UserProgress,Question,Quiz,UserAnswer,Contactus
from database import session as db_session
from sqlalchemy.exc import IntegrityError,PendingRollbackError
import base64
import json
import datetime
import matplotlib.pyplot as plt
import os
from werkzeug.utils import secure_filename
app = Flask(__name__)
api = Api(app)
app.secret_key = 'LMSFYNDCAPSTONE_PROJECT_F4I3AL_!M4M'

# Home Route
import base64

import base64

@app.route('/')
def index_page():
    username = session.get('username')
    role=session.get('role')
    blogs = db_session.query(Blogpost).all()
    for blog in blogs:
        # Ensure there is no extra static/ prefix
        blog.thumbnail = blog.thumbnail.replace('\\', '/')  # Fix backslashes
        if blog.thumbnail.startswith('static/'):
            blog.thumbnail = blog.thumbnail[len('static/'):]
    courses = db_session.query(Course).all()

    # Convert the course_thumbnail to base64
    for course in courses:
        if course.course_thumbnail:
            # Convert binary data to base64
            course.course_thumbnail_base64 = base64.b64encode(course.course_thumbnail).decode('utf-8')
        else:
            course.course_thumbnail_base64 = None

    return render_template('index.html', username=username, blogs=blogs, courses=courses,role=role)

@app.route('/aboutus/')
def aboutus():
    username = session.get('username')

    return render_template('aboutus.html',username=username)
@app.route('/contactus/', methods=['GET', 'POST'])
def contactus():
    username = session.get('username')  # Assuming you're using a session-based username
    
    if request.method == 'POST':
        # Get form data
        name = request.form.get('name')
        email = request.form.get('email')
        info = request.form.get('info')

        # Basic validation
        if not name or not email or not info:
            flash("Please fill in all fields.", "error")
            return redirect(url_for('contactus'))

        # Save to database
        new_contact = Contactus(name=name, email=email, info=info)
        db_session.add(new_contact)
        db_session.commit()

        flash("Your message has been sent successfully.", "success")
        return redirect(url_for('contactus'))  # Redirect to the same page or another page

    return render_template('contact.html', username=username)


# Login Page
@app.get('/login')
def get_login():
    return render_template('login.html')

@app.route('/blogs/')
def blogs():
    
    blogs = db_session.query(Blogpost).all()
    for blog in blogs:
        # Ensure there is no extra static/ prefix
        blog.thumbnail = blog.thumbnail.replace('\\', '/')  # Fix backslashes
        if blog.thumbnail.startswith('static/'):
            blog.thumbnail = blog.thumbnail[len('static/'):]

    return render_template ('blogs.html',blogs=blogs)
@app.route('/blogs/<int:id>')
def showblogs(id):
    blog = db_session.query(Blogpost).filter_by(id=id).first()
    blog.thumbnail = blog.thumbnail.replace('\\', '/')  # Fix backslashes
    if blog.thumbnail.startswith('static/'):
         blog.thumbnail = blog.thumbnail[len('static/'):]

    return render_template('showblog.html', blog=blog)


@app.post('/login')
def user_login():
    email = request.form.get('Email')
    password = request.form.get('Password')

    # Check if the user exists in the database
    user = db_session.query(User).filter_by(email=email).first()

    if user:
        # Verify the password
        if check_password_hash(user.password, password):
            # Store user information in the session
            session['username'] = user.username
            session['role'] = user.role
            session['id'] = user.id 

            if user.role == 'student':
                return render_template('index.html', username=user.username)
            elif user.role == 'admin':
                return redirect(url_for('admin_dashboard'))
            else:
                return render_template('index.html', username=None)
        else:
            return render_template('login.html', error="Incorrect password. Please try again.")
    else:
        return render_template('login.html', error="We can't find your credentials. Kindly sign up with a new account.")

@app.route('/signin/',methods=['GET','POST'])

def signin():
    if request.method=='POST':
        name = request.form.get('Username')
        email = request.form.get('Email')
        password = request.form.get('Password')
        confirm_password = request.form.get('ConfirmPassword')

    # Check if passwords match
        if password != confirm_password:
            return render_template('signup.html', error="Passwords do not match!")

        role = 'student'
    
    # Check if the email already exists
        existing_email = db_session.query(User).filter_by(email=email).first()
        if existing_email:
            return render_template('signup.html', error="The Email already exists. Kindly choose another Email.")

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(username=name, email=email, role=role, password=hashed_password)
        # admin_pass="admin@codify123"
        # admin_hash= generate_password_hash(admin_pass, method='pbkdf2:sha256')
        # new_admin=User(username='admin',email="admin@codify.com",role='admin',password=admin_hash)
        # db_session.add(new_admin)
        db_session.add(new_user)

        try:
            db_session.commit()
            return render_template('signup.html', success="Account created successfully!")
        except IntegrityError as e:
            db_session.rollback()
            return render_template('signup.html', error=f"An error occurred: {e}")

    return render_template('signup.html')

from sqlalchemy import func


#--------------------------COURSES VIEWS----------------------------------------------->
@app.route('/user/quizzes')
def user_quizzes():
    session_id = session.get('id')  # Get the current user's ID from the session
    username=session.get('username')
    quizzes = db_session.query(Quiz).all()  # Fetch all quizzes
    quizzes_with_progress = []

    for quiz in quizzes:
        progress = 0
        score = 0
        total_questions = len(quiz.questions)

        # Get user progress for the current quiz
        user_progress = db_session.query(UserProgress).filter_by(
            user_id=session_id, quiz_id=quiz.id
        ).first()

        if user_progress:
            score = user_progress.quiz_score
            progress = (user_progress.questions_answered / total_questions) * 100

        quizzes_with_progress.append({
            'id': quiz.id,
            'title': quiz.title,
            'score': score,
            'progress': progress
        })

    return render_template('user_quizzes.html', quizzes=quizzes_with_progress,username=username)


# Route to display the quiz and its questions
@app.route('/submit_quiz/<int:quiz_id>', methods=['GET', 'POST'])
def submit_quiz(quiz_id):
    session_id = session.get('id')  # Get the user's ID from the session
    quiz = db_session.query(Quiz).filter_by(id=quiz_id).first()

    if not quiz:
        return "Quiz not found", 404

    if request.method == 'POST':
        correct_answers = 0
        for question in quiz.questions:
            question_key = f"question_{question.id}"
            if question_key in request.form:
                user_answer = int(request.form[question_key])
                if user_answer == question.correct_option:
                    correct_answers += 1

        total_questions = len(quiz.questions)
        score = (correct_answers / total_questions) * 100  # Percentage score

        # Assuming quiz is associated with a course
        course_id = quiz.course_id  # Update based on your schema

        # Update or create user progress
        user_progress = db_session.query(UserProgress).filter_by(
            user_id=session_id, quiz_id=quiz.id
        ).first()

        if not user_progress:
            user_progress = UserProgress(
                user_id=session_id,
                quiz_id=quiz.id,
                course_id=course_id,
                quiz_score=score,
                questions_answered=total_questions
            )
            db_session.add(user_progress)
        else:
            user_progress.quiz_score = score
            user_progress.questions_answered = total_questions

        db_session.commit()

        return redirect(url_for('user_quizzes'))

    return render_template('submit_quiz.html', quiz=quiz)

#students courses dashboard
@app.route('/courses/')
def courses():
    username = session.get('username')
    courses=db_session.query(Course).all()
    # if 'username' not in session or session.get('role') != 'admin' or 'student' :
    #     return render_template('courses.html',no_enroll="Please Login as Student to Access the course",all_course=all_course)
    for course in courses:
        course.thumbnail=base64.b64encode(course.course_thumbnail).decode("utf-8")
    return render_template('courses.html',courses=courses,username=username)
@app.route('/course_lessons/<int:id>')
def course_lessons(id):
    username = session.get('username')

    course = db_session.query(Course).filter_by(id=id).first()
    
    
    if not course:
        return "Course not found", 404
    
    return render_template('course_lessons.html', course=course,username=username)
import os

@app.route('/allblogs/admin')
def showallblogs():
    if 'username' not in session or session.get('role') != 'admin':
        return redirect(url_for('get_login'))
    blogs = db_session.query(Blogpost).all()
    
    # Normalize the paths
    for blog in blogs:
        # Ensure there is no extra static/ prefix
        blog.thumbnail = blog.thumbnail.replace('\\', '/')  # Fix backslashes
        if blog.thumbnail.startswith('static/'):
            blog.thumbnail = blog.thumbnail[len('static/'):]

    return render_template('showadminblogs.html', blogs=blogs)
@app.route('/updateblog/<int:id>', methods=['GET', 'POST'])
def updateblog(id):
    if 'username' not in session or session.get('role') != 'admin':
        return redirect(url_for('get_login'))

    blog = db_session.query(Blogpost).filter_by(id=id).first()

    if not blog:
        flash("Blog not found!", "danger")
        return redirect(url_for('showallblogs'))

    if request.method == 'POST':
        blog.title = request.form['title']
        blog.description = request.form['description']
        
        # Handle thumbnail update if a new image is uploaded
        if 'thumbnail' in request.files:
            file = request.files['thumbnail']
            if file.filename:
                filename = os.path.join('static/blogs/thumbnail', file.filename)
                file.save(filename)
                blog.thumbnail = filename  # Update blog thumbnail path

        db_session.commit()
        flash("Blog updated successfully!", "success")
        return redirect(url_for('showallblogs'))

    return render_template('updateblog.html', blog=blog)



@app.route('/deleteblog/<int:id>')
def deleteblog(id):
    if 'username' not in session or session.get('role') != 'admin':
        return redirect(url_for('get_login'))
    blog = db_session.query(Blogpost).filter_by(id=id).first()
    if blog:
        db_session.delete(blog)
        db_session.commit()
        return redirect(url_for('showallblogs'))  # Use the function name 'showallblogs' here

@app.route('/courses/course_description/<int:id>')
def course_description(id):
    username = session.get('username')
    course = db_session.query(Course).filter_by(id=id).first()
    if course:
        course.thumbnail = base64.b64encode(course.course_thumbnail).decode("utf-8")
    return render_template("course_description.html", course=course,username=username)
@app.route('/enroll/<int:course_id>', methods=['POST', 'GET'])
def enroll_in_course(course_id):
    username = session.get('username')
    if 'username' not in session or session.get('role') != 'student':
        flash("Please log in as a student to enroll in courses.", "error")
        return redirect(url_for('courses'))

    # Get logged-in user
    username = session.get('username')
    user = db_session.query(User).filter_by(username=username).first()
    if not user:
        flash("User not found.", "error")
        return redirect(url_for('courses'))

    # Check if the course exists
    course = db_session.query(Course).filter_by(id=course_id).first()
    if not course:
        flash("Course not found.", "error")
        return redirect(url_for('courses'))

    # Check if user is already enrolled
    existing_enrollment = db_session.query(Enrollment).filter_by(user_id=user.id, course_id=course.id).first()
    if existing_enrollment:
        flash("You are already enrolled in this course.", "info")
        return redirect(url_for('course_lessons', id=course_id))

    # Create new enrollment
    new_enrollment = Enrollment(user_id=user.id, course_id=course.id)
    db_session.add(new_enrollment)

    try:
        db_session.commit()
        return render_template("course_lesson.html",success=f"You have Successfully Enrolled in {course.title}")
        
    except Exception as e:
        db_session.rollback()
        flash(f"An error occurred while enrolling: {e}", "error")

    # Redirect to the course lessons page
    return redirect(url_for('course_lessons', id=course_id))

@app.route('/admin/quiz/create', methods=['GET', 'POST'])
def create_quiz():
    if 'username' not in session or session.get('role') != 'admin':
        return redirect(url_for('get_login'))
    if request.method == 'POST':
        title = request.form.get('title')
        course_id = request.form.get('course_id')

        if not course_id:
            return "Course ID is required", 400

        # Create a new Quiz
        new_quiz = Quiz(title=title, course_id=int(course_id))
        db_session.add(new_quiz)
        db_session.commit()
        return redirect('/admin/quizzes')

    # Fetch all courses to display in the dropdown
    courses = db_session.query(Course).all()
    return render_template('create_quiz.html', courses=courses)

@app.route('/admin/quiz/<int:quiz_id>/add_question', methods=['GET', 'POST'])
def add_question(quiz_id):
    if 'username' not in session or session.get('role') != 'admin':
        return redirect(url_for('get_login'))
    quiz = db_session.query(Quiz).filter_by(id=quiz_id).first()
    if not quiz:
        return "Quiz not found", 404

    if request.method == 'POST':
        question_text = request.form.get('question_text')
        option_1 = request.form.get('option_1')
        option_2 = request.form.get('option_2')
        option_3 = request.form.get('option_3')
        option_4 = request.form.get('option_4')
        correct_option = request.form.get('correct_option')

        if not all([question_text, option_1, option_2, option_3, option_4, correct_option]):
            flash("All fields are required!", "danger")
            return redirect(url_for('add_question', quiz_id=quiz_id))

        new_question = Question(
            question_text=question_text,
            option_1=option_1,
            option_2=option_2,
            option_3=option_3,
            option_4=option_4,
            correct_option=int(correct_option),
            quiz_id=quiz_id
        )
        db_session.add(new_question)
        db_session.commit()

        flash("Question added successfully!", "success")
        return redirect(url_for('manage_questions', quiz_id=quiz_id))

    return render_template('add_questions.html', quiz=quiz)
@app.route('/admin/quizzes', methods=['GET', 'POST'])
def manage_quizzes():
    if 'username' not in session or session.get('role') != 'admin':
        return redirect(url_for('get_login'))
    if request.method == 'POST':
        # Handle quiz deletion
        quiz_id = request.form.get('quiz_id')
        quiz = db_session.query(Quiz).get(quiz_id)
        if quiz:
            db_session.delete(quiz)
            db_session.commit()
            flash('Quiz deleted successfully!', 'success')
        else:
            flash('Quiz not found!', 'danger')
        return redirect(url_for('manage_quizzes'))

    quizzes = db_session.query(Quiz).all()
    return render_template('manage_quizzes.html', quizzes=quizzes)
@app.route('/admin/quiz/<int:quiz_id>/questions', methods=['GET'])
def manage_questions(quiz_id):
    if 'username' not in session or session.get('role') != 'admin':
        return redirect(url_for('get_login'))
    quiz = db_session.query(Quiz).filter_by(id=quiz_id).first()
    if not quiz:
        return "Quiz not found", 404

    questions = db_session.query(Question).filter_by(quiz_id=quiz_id).all()
    return render_template('manage_questions.html', quiz=quiz, questions=questions)

@app.route('/progress', methods=['GET'])
def user_progress():
    username = session.get('username')
    user = db_session.query(User).filter_by(username=username).first()

    if not user:
        return redirect(url_for('login'))

    progress = db_session.query(UserProgress).filter_by(user_id=user.id).all()
    return render_template('progress.html', progress=progress)


#-------------------------------Admin Views--------------------------------->
# Admin Dashboard with Access Control
from io import BytesIO
from sqlalchemy.orm import joinedload

@app.route('/admin/show-users/')
def show_users():
    if 'username' not in session or session.get('role') != 'admin':
        return redirect(url_for('get_login'))
    try:
        # Query the users and their enrollments
        users = db_session.query(User).all()
        
        
        # Determine how many users are enrolled vs. not enrolled
        enrolled_count = sum(1 for user in users if len(user.enrollments) > 0)
        not_enrolled_count = len(users) - enrolled_count

        # Data for pie chart (Enrolled vs Not Enrolled)
        labels = ['Enrolled', 'Not Enrolled']
        sizes = [enrolled_count, not_enrolled_count]
        colors = ['#5e0dd9', '#ff5733']  # Purple for enrolled, Red for not enrolled

        # Log the data for debugging
        print(f"Enrolled Count: {enrolled_count}")
        print(f"Not Enrolled Count: {not_enrolled_count}")

        # Initialize Matplotlib
        import matplotlib
        matplotlib.use('Agg')  # Non-GUI backend for servers
        import matplotlib.pyplot as plt

        # Create a pie chart for enrollment status
        plt.figure(figsize=(8, 8))
        plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=140, wedgeprops={'edgecolor': 'black'})
        plt.title('Enrollment Status')

        # Save the pie chart as Base64 for rendering
        img = BytesIO()
        plt.savefig(img, format='png')
        img.seek(0)
        plot_url = base64.b64encode(img.getvalue()).decode()
        plt.close()

        # Render the template with the users data and the plot
        return render_template('showusers.html', users=users, plot_url=plot_url)

    except Exception as e:
        print(f"Error generating plot: {e}")
        return "Error generating plot", 500


@app.route('/admin/show-courses/')
def show_courses():
    if 'username' not in session or session.get('role') != 'admin':
        return redirect(url_for('get_login'))
    try:
        courses = db_session.query(Course).all()
        for course in courses:
            course.thumbnail = base64.b64encode(course.course_thumbnail).decode("utf-8")
        return render_template('showcourses.html', courses=courses)
    except IntegrityError as e:
        db_session.rollback()  # Rollback the session on integrity error
        return "An error occurred: " + str(e)
    
@app.route('/admin/deletecourse/<int:id>',methods=['POST'])
def deletecourse(id):
    if 'username' not in session or session.get('role') != 'admin':
        return redirect(url_for('get_login'))
    course=db_session.query(Course).get(id)
    db_session.delete(course)
    db_session.commit()
    return redirect(url_for('show_courses',Success="Successfully deleted"))

@app.route('/admin/update_course/<int:course_id>/', methods=['GET', 'POST'])
def update_course(course_id):
    course = db_session.query(Course).filter_by(id=course_id).first()
    if not course:
        return "Course not found", 404

    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        
        if not title or not description:
            flash("Title and Description are required.", "error")
            return redirect(url_for('update_course', course_id=course_id))
        
        # Update course details
        course.title = title
        course.description = description

        if 'Thumbnail' in request.files:
            thumbnail = request.files['Thumbnail'].read()
            if thumbnail:
                course.course_thumbnail = thumbnail

        # Extract lessons
        lessons = []
        index = 0
        while True:
            lesson_title = request.form.get(f'lessons[{index}][title]')
            lesson_content = request.form.get(f'lessons[{index}][content]')
            lesson_link = request.form.get(f'lessons[{index}][course_link]')

            if not lesson_title:
                break

            lessons.append({
                'title': lesson_title,
                'content': lesson_content,
                'course_link': lesson_link
            })
            index += 1

        # Remove existing lessons and add updated ones
        db_session.query(Lesson).filter_by(course_id=course_id).delete()

        for lesson in lessons:
            updated_lesson = Lesson(
                title=lesson['title'],
                content=lesson['content'],
                course_link=lesson['course_link'],
                course_id=course.id
            )
            db_session.add(updated_lesson)

        db_session.commit()
        print("Course Updated")
        return redirect(url_for('index_page'))

    existing_lessons = db_session.query(Lesson).filter_by(course_id=course_id).all()
    return render_template('updatecourse.html', course=course, lessons=existing_lessons)

@app.route('/admin/add_course/', methods=['GET', 'POST'])
def add_course():
    
    if 'username' not in session or session.get('role') != 'admin':
        return redirect(url_for('get_login'))
    if request.method == 'POST':
        # Get course data
        title = request.form['title']
        description = request.form['description']
        course_thumbnail = request.files['Thumbnail'].read()

        # Collect lessons from JSON-formatted data sent with the form
        lessons_data = request.form.get('lessons')
        lessons_list = eval(lessons_data)  # Convert string to Python list

        # Create course instance
        new_course = Course(title=title, description=description,course_thumbnail=course_thumbnail )
        db_session.add(new_course)
        db_session.commit()

        # Add lessons
        for lesson in lessons_list:
            new_lesson = Lesson(
                title=lesson['title'],
                content=lesson['content'],
                course_link=lesson['course_link'],
                course_id=new_course.id
            )
            db_session.add(new_lesson)
        db_session.commit()
        print("Courses Added")
        return redirect(url_for('index_page'))

  
    return render_template('addcourse.html')


UPLOAD_FOLDER = 'static/blogs/thumbnail'  # Ensure this is the correct path
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/admin/addblog/', methods=['GET', 'POST'])
def addblog():
    
    if 'username' not in session or session.get('role') != 'admin':
        return redirect(url_for('get_login'))
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('Description')
        category = request.form.get('category')
        print("Runned 1")

        if 'Thumbnail' not in request.files:
            return render_template('addblog.html', error='No file part')

        file = request.files['Thumbnail']

        if file.filename == '':
            return render_template('addblog.html', error='No selected file')

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            
            print("Runned 1")
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)

            file.save(file_path)
            print("Runned 1")

            blog = Blogpost(
                title=title,
                category=category,
                description=description,
                thumbnail=file_path  # Save the file path
            )

            try:
                db_session.add(blog)
                db_session.commit()
                print("added")
                return render_template('addblog.html', success=f'{title} successfully added to the Blog page')
            except Exception as e:
                print(f"Error occurred: {e}")
                db_session.rollback()
                return render_template('addblog.html', error='There was an error while uploading the Blog page')

    return render_template('addblog.html')
@app.route('/admin/')
def admin_dashboard():
    if 'username' not in session or session.get('role') != 'admin':
        return redirect(url_for('get_login'))

    try:
        # Query the total number of users, courses, and students
        users = db_session.query(User).all()
        courses = db_session.query(Course).all()
        students = db_session.query(User).filter_by(role='student').count()

        user_count = students
        courses_count = len(courses)

        # Query the users and their enrollments
        users = db_session.query(User).all()
        
        # Determine how many users are enrolled vs. not enrolled
        enrolled_count = sum(1 for user in users if len(user.enrollments) > 0)
        not_enrolled_count = len(users) - enrolled_count

        # Data for pie chart (Enrolled vs Not Enrolled)
        labels = ['Enrolled', 'Not Enrolled']
        sizes = [enrolled_count, not_enrolled_count]
        colors = ['#5e0dd9', '#ff5733']  # Purple for enrolled, Red for not enrolled

        # Log the data for debugging
        print(f"Enrolled Count: {enrolled_count}")
        print(f"Not Enrolled Count: {not_enrolled_count}")

        # Initialize Matplotlib
        import matplotlib
        matplotlib.use('Agg')  # Non-GUI backend for servers
        import matplotlib.pyplot as plt

        # Create a pie chart for enrollment status
        plt.figure(figsize=(8, 8))
        plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=140, wedgeprops={'edgecolor': 'black'})
        plt.title('Enrollment Status')

        # Save the pie chart as Base64 for rendering
        img = BytesIO()
        plt.savefig(img, format='png')
        img.seek(0)
        plot_url = base64.b64encode(img.getvalue()).decode()
        plt.close()

        # Render the template with the necessary data
        return render_template(
            'admin.html',
            users=users,
            courses=courses,
            user_count=user_count,
            courses_count=courses_count,
            plot_url=plot_url,
            enrolled_count=enrolled_count
        )

    except Exception as e:
        print(f"Error generating plot: {e}")
        return "Error generating plot", 500

#---------------------------------------ADMIN VIEWS END---------------------------> 


def total_lessons_in_course(course_id):
    # Query the database to get the total number of lessons in the course
    return db_session.query(Lesson).filter_by(course_id=course_id).count()

@app.route('/certificate/<int:quiz_id>')
def certificate(quiz_id):
    user = session.get('username')
    time = datetime.datetime.now().strftime('%d-%m-%y')

    # Fetch the quiz title or course name using the quiz_id
    quiz = db_session.query(Quiz).filter_by(id=quiz_id).first()

    if not quiz:
        flash("Invalid quiz for certificate generation.", "danger")
        return redirect(url_for('user_quizzes'))

    # Check user progress to ensure eligibility
    user_progress = db_session.query(UserProgress).filter_by(user_id=session.get('id'), quiz_id=quiz_id).first()

    if user_progress and user_progress.quiz_score >= 70:
        course_name = quiz.title  # Assuming title represents the course name
        return render_template('certificate.html', user=user, time=time, course_name=course_name)
    else:
        flash("You are not eligible for a certificate for this quiz.", "warning")
        return redirect(url_for('user_quizzes'))

# Logout Route
@app.route('/logout')
def logout():
    session.clear()  # Clear the session
    return redirect(url_for('index_page'))


if __name__ == "__main__":
    app.run(debug=True)  # Ensure using 127.0.0.1 instead of 0.0.0.0
