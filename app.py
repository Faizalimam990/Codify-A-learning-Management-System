from flask import Flask, request, render_template, redirect, url_for, session,flash
from flask_restful import Resource, Api
from werkzeug.security import generate_password_hash, check_password_hash
from models import User, Course,Lesson,Blogpost,Enrollment
from database import session as db_session
from sqlalchemy.exc import IntegrityError,PendingRollbackError
import base64
import json
import datetime
import os
from werkzeug.utils import secure_filename
app = Flask(__name__)
api = Api(app)
app.secret_key = 'LMSFYNDCAPSTONE_PROJECT_F4I3AL_!M4M'

# Home Route
import base64
@app.route('/')
def index_page():
    username = session.get('username')
    blogs=db_session.query(Blogpost).all()
    course=db_session.query(Course).all()

    return render_template('index.html', username=username,blogs=blogs,course=course)

    



# Login Page
@app.get('/login')
def get_login():
    return render_template('login.html')


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
# Route to display the signup page

# @app.route('/signup/', methods=['GET'])
# def signin_page():
#     return render_template('signup.html')

# # Route to handle the signup form submission
# @app.route('/signin/', methods=['POST'])
# def user_signin():
#     name = request.form.get('Username')
#     email = request.form.get('Email')
#     password = request.form.get('Password')
#     confirm_password = request.form.get('ConfirmPassword')

#     # Check if passwords match
#     if password != confirm_password:
#         return render_template('signup.html', error="Passwords do not match!")

#     role = 'student'
    
#     # Check if the email already exists
#     existing_email = db_session.query(User).filter_by(email=email).first()
#     if existing_email:
#         return render_template('signup.html', error="The Email already exists. Kindly choose another Email.")

#     hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
#     new_user = User(username=name, email=email, role=role, password=hashed_password)
#     db_session.add(new_user)

#     try:
#         db_session.commit()
#         return render_template('signup.html', success="Account created successfully!")
#     except IntegrityError as e:
#         db_session.rollback()
#         return render_template('signup.html', error=f"An error occurred: {e}")

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
        db_session.add(new_user)

        try:
            db_session.commit()
            return render_template('signup.html', success="Account created successfully!")
        except IntegrityError as e:
            db_session.rollback()
            return render_template('signup.html', error=f"An error occurred: {e}")

    return render_template('signup.html')



#--------------------------COURSES VIEWS----------------------------------------------->

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
    course = db_session.query(Course).filter_by(id=id).first()
    
    if not course:
        return "Course not found", 404
    
    return render_template('course_lessons.html', course=course)
@app.route('/courses/course_description/<int:id>')
def course_description(id):
    username = session.get('username')
    course = db_session.query(Course).filter_by(id=id).first()
    if course:
        course.thumbnail = base64.b64encode(course.course_thumbnail).decode("utf-8")
    return render_template("course_description.html", course=course,username=username)
@app.route('/enroll/<int:course_id>', methods=['POST', 'GET'])
def enroll_in_course(course_id):
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
        flash(f"Successfully enrolled in {course.title}!", "success")
    except Exception as e:
        db_session.rollback()
        flash(f"An error occurred while enrolling: {e}", "error")

    # Redirect to the course lessons page
    return redirect(url_for('course_lessons', id=course_id))

#-------------------------------Admin Views--------------------------------->
# Admin Dashboard with Access Control
@app.route('/admin/show-users/')
def show_users():
    # if 'username' not in session or session.get('role') != 'admin':
    #     return redirect(url_for('get_login'))
    users = db_session.query(User).all()
    
    return render_template('showusers.html')


@app.route('/admin/show-courses/')
def show_courses():
    if 'username' not in session or session.get('role') != 'admin':
        return redirect(url_for('get_login'))
    courses = db_session.query(Course).all()
    for course in courses:
        course.thumbnail=base64.b64encode(course.course_thumbnail).decode("utf-8")
    return render_template('showcourses.html',courses=courses)

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
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['Description']
        category = request.form['category']

        if 'Thumbnail' not in request.files:
            return render_template('addblog.html', error='No file part')

        file = request.files['Thumbnail']

        if file.filename == '':
            return render_template('addblog.html', error='No selected file')

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            
            # Ensure the upload folder exists
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)

            file.save(file_path)

            # Save the file path instead of binary data
            blog = Blogpost(
                title=title,
                category=category,
                description=description,
                thumbnail=file_path  # Save the file path
            )

            try:
                db_session.add(blog)
                db_session.commit()
                return render_template('addblog.html', success=f'{title} successfully added to the Blog page')
            except Exception as e:
                print(f"Error occurred: {e}")
                db_session.rollback()
                return render_template('addblog.html', error='There was an error while uploading the Blog page')

    return render_template('addblog.html')


@app.route('/admin/') 
def admin_dashboard():
    # Check if the user is logged in and is an admin
    # if 'username' not in session or session.get('role') != 'admin':
    #     return redirect(url_for('get_login'))

    users = db_session.query(User).all()
    courses = db_session.query(Course).all()
    students=db_session.query(User).filter_by(role='student').count()
    user_count=students
    courses_count=len(courses)
    print(courses_count)

    return render_template('admin.html', users=users, courses=courses,user_count=user_count,courses_count=courses_count)

#---------------------------------------ADMIN VIEWS END---------------------------> 




@app.route('/certificate/')
def certificate():
    user=session.get('username')
    time = datetime.datetime.now().strftime('%d-%m-%y')
    return render_template('certificate.html',user=user,time=time)


# Logout Route
@app.route('/logout')
def logout():
    session.clear()  # Clear the session
    return redirect(url_for('index_page'))


if __name__ == '__main__':  
    app.run(debug=True)
