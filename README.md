# Learning Management System (LMS) - Flask

## 📌 Project Overview
This is a full-featured Learning Management System (LMS) built using Flask. It allows users to sign in, enroll in courses, watch video lessons, take quizzes, and receive certificates upon successful completion. The admin panel provides complete control over quizzes, lessons, courses, and blogs.

## 🎬 Video Overview
https://github.com/user-attachments/assets/f7da555a-3e23-4ea1-b889-4eab07091f66

## 🚀 Features
- **User Authentication**: Sign up, login, and manage user profiles.
- **Course Enrollment**: Users can browse and enroll in available courses.
- **Video Lessons**: Courses include structured video lessons for learning.
- **Quiz System**: Users can take quizzes and receive instant feedback.
- **User Analytics**: Student progress is tracked and visualized using Matplotlib.
- **Certification**: Users receive certificates upon quiz completion.
- **Admin Dashboard**:
  - Manage courses (Add, Delete, Update)
  - Manage quizzes (Create, Delete, Modify)
  - Manage blogs (Create, Delete, Update)
  - View and analyze student data

## 🛠️ Technologies Used
- **Flask**: Backend framework
- **SQLAlchemy**: Database ORM
- **Matplotlib**: Data visualization for student analytics
- **Bootstrap**: Frontend styling

## 🏗️ LMS Architecture Diagram
![LMS Architecture](https://i.imgur.com/4LZnwUZ.png)



## 📂 Project Structure
```
LMS-Flask/
│── static/
│   ├── blogs/
│   ├── images/
│   ├── js/
│   ├── styles/
│   │   ├── styles.css
│
│── templates/
│   ├── aboutus.html
│   ├── add_questions.html
│   ├── addblog.html
│   ├── addcourse.html
│   ├── admin.html
│   ├── adminsidebar.html
│   ├── blogs.html
│   ├── certificate.html
│   ├── contact.html
│   ├── course_description.html
│   ├── course_lessons.html
│   ├── courses.html
│   ├── create_quiz.html
│   ├── footer.html
│   ├── index.html
│   ├── login.html
│   ├── manage_questions.html
│   ├── manage_quizzes.html
│   ├── nav.html
│   ├── quiz.html
│   ├── showadminblogs.html
│   ├── showblog.html
│   ├── showcourses.html
│   ├── showusers.html
│   ├── signup.html
│   ├── student.html
│   ├── submit_quiz.html
│   ├── updateblog.html
│   ├── updatecourse.html
│   ├── user_quizzes.html
│
│── app.py  # Main Flask app
│── database.py  # Database models
│── models.py  # SQLAlchemy models
│── database.db  # SQLite database
│── README.md  # Project documentation
│── requirements.txt  # Dependencies
```

## 🏗️ Installation Guide
1. Clone the repository:
   ```sh
   git clone https://github.com/Faizalimam990/Codify-A-learning-Management-System
   cd Codify-A-learning-Management-System
   ```
2. Create a virtual environment:
   ```sh
   python -m venv venv
   source venv/bin/activate  # For macOS/Linux
   venv\Scripts\activate  # For Windows
   ```
3. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
4. Run the Flask app:
   ```sh
   python app.py
   ```
5. Open the browser and visit:
   ```sh
   http://127.0.0.1:5000
   ```

## 📜 License
This project is licensed under the MIT License.
