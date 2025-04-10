import os, requests, sqlite3, re, datetime, pytz

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, url_for, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required

# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///learnway.db")

def obtener_fecha_venezuela():
    """Obtiene la fecha actual en la zona horaria de Venezuela en formato YYYY-MM-DD."""
    zona_horaria_venezuela = pytz.timezone('America/Caracas')
    fecha_utc = datetime.datetime.now(datetime.UTC)
    fecha_venezuela = fecha_utc.replace(tzinfo=pytz.utc).astimezone(zona_horaria_venezuela)
    return fecha_venezuela.strftime('%Y-%m-%d')

@app.after_request
def after_request(response):
    # Ensure responses aren't cached
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    
    return response

# Home
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":

        return render_template("index.html")
    
    else:

        courses = db.execute("""
            SELECT id, title, card_description, course_img
            FROM courses                     
        """)
        return render_template("index.html", courses=courses)
    

@app.route("/register", methods=["GET", "POST"])
def register():
    # Register user
    if request.method == "POST":

        names = request.form.get("names")
        surnames = request.form.get("surnames")
        email = request.form.get("email")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        default_profile = "https://static.vecteezy.com/system/resources/thumbnails/009/292/244/small/default-avatar-icon-of-social-media-user-vector.jpg"

        # Validations
        if not names or not surnames or not email or not password or not confirmation:
            flash("All fields need to be filled", 'error')
            return render_template("register.html", names=names, surnames=surnames, email=email, password=password, confirmation=confirmation)
        
        if not re.match(r"^[a-zA-Z]+$", names) or not re.match(r"^[a-zA-Z]+$", surnames):
            flash("Invalid names/surnames", 'error')
            return render_template("register.html", names=names, surnames=surnames, email=email, password=password, confirmation=confirmation)
        
        if password == confirmation:
            password = generate_password_hash(confirmation, method='scrypt', salt_length=16)            
        else:
            flash("Both passwords don't match", 'error')
            return render_template("register.html", names=names, surnames=surnames, email=email, password=password, confirmation=confirmation)
        
        try:
            db.execute("""
                INSERT INTO users (names, surnames, email, hash, profile_img)
                VALUES(?, ?, ?, ?, ?)
            """, names, surnames, email, password, default_profile)     
            flash("Successfully registered!", 'success')
            return redirect("/login")       
        except ValueError:
            flash("Registered username", 'error')
            return render_template("register.html", names=names, surnames=surnames, email=email, password=password, confirmation=confirmation)

    else:

        return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        if not email or not password:
            flash("All fields need to be filled", 'error')
            return render_template("login.html", email=email, password=password)

        # session["role"] = "student"

        # Query database for credentials
        user = db.execute("SELECT id, names, surnames, hash, profile_img FROM users WHERE email = ?", email)

        # Ensure username exists and password is correct
        if len(user) != 1 or not check_password_hash(user[0]["hash"], password):
            flash("Invalid username and/or password", 'error')
            return render_template("login.html", email=email, password=password)
        
        # Remember which user has logged in
        session["user_id"] = user[0]["id"]
        session["names"] = f'{user[0]["names"]} {user[0]["surnames"]}'
        session["profile_img"] = user[0]["profile_img"]

        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/course_preview/<int:course_id>", methods=["GET", "POST"])
def course_preview(course_id):
    if request.method == "POST":
        # Obtener los datos del formulario
        rating = request.form.get("rating")
        comment = request.form.get("comment")
        course_id_form = request.form.get("course_id")

        # Validar que los campos no estén vacíos
        if not rating or not comment:
            flash("All fields must be filled!", "error")
            return redirect(f"/course_preview/{course_id}")

        # Insertar la reseña en la base de datos
        db.execute("""
            INSERT INTO comments (user_id, course_id, comment, rating)
            VALUES (?, ?, ?, ?)
        """, session["user_id"], course_id_form, comment, int(rating))

        flash("Review submitted successfully!", "success")
        return redirect(f"/course_preview/{course_id}")

    else:
        # Obtener información del curso
        course_preview = db.execute("""
            SELECT id, title, preview_description, course_img
            FROM courses
            WHERE id = ?                        
        """, course_id)

        # Validar si el curso existe
        if not course_preview:
            flash("Course not found!", "error")
            return redirect("/")

        # Obtener los módulos del curso
        course_modules = db.execute("""
            SELECT order_course, module_title, info
            FROM modules
            WHERE course_id = ?
            ORDER BY order_course                        
        """, course_id)

        # Obtener los comentarios existentes
        comments = db.execute("""
            SELECT users.names, users.surnames, comments.comment, comments.rating
            FROM comments
            JOIN users ON comments.user_id = users.id
            WHERE comments.course_id = ?                                        
        """, course_id)

        return render_template("course_preview.html", course_preview=course_preview, course_modules=course_modules, comments=comments)


@app.route('/profile_settings', methods=['GET', 'POST'])
@login_required
def profile_settings():
    if request.method == "POST":
        # Obtener los datos enviados por el formulario
        first_name = request.form.get('names')
        last_name = request.form.get('surnames')
        email = request.form.get('email')
        password = request.form.get('password')
        profile_img = request.files.get('profile_img')

        # Validar y actualizar solo los campos enviados
        updates = {}
        if first_name:
            updates['names'] = first_name
        if last_name:
            updates['surnames'] = last_name
        if email:
            updates['email'] = email
        if password:
            # Generar un hash para la nueva contraseña
            updates['hash'] = generate_password_hash(password, method='scrypt', salt_length=16)
        if profile_img:
            if not profile_img.filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                flash("Formato de imagen no válido. Solo se permiten archivos PNG, JPG o JPEG.", "error")
                return redirect(url_for('profile_settings'))
            # Guardar la imagen en la carpeta uploads
            filename = f"{session['user_id']}_{profile_img.filename}"
            filepath = os.path.join("static/uploads", filename)
            profile_img.save(filepath)
            # Guardar la ruta relativa en la base de datos
            updates['profile_img'] = f"/static/uploads/{filename}"


        # Construir la consulta SQL dinámicamente
        if updates:
            set_clause = ", ".join([f"{key} = ?" for key in updates.keys()])
            values = list(updates.values())
            values.append(session["user_id"])  # Agregar el user_id al final para el WHERE
            db.execute(f"UPDATE users SET {set_clause} WHERE id = ?", *values)

        # Actualizar la sesión con los nuevos datos
        if 'names' in updates:
            session['names'] = f"{updates.get('names', session['names'])} {updates.get('surnames', '').strip()}"
        if 'profile_img' in updates:
            session['profile_img'] = updates['profile_img']

        flash("Perfil actualizado exitosamente", "success")
        return redirect(url_for('profile_settings'))

    else:
        # Obtener información de perfil del usuario
        user = db.execute("""
            SELECT names, surnames, email, profile_img
            FROM users
            WHERE id = ?                        
        """, session["user_id"])

        return render_template('profile_settings.html', user=user)


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/my_learning", methods=["GET", "POST"])
@login_required
def subjects():
    if request.method == "POST":

        return redirect("/")
        
    else:  

        my_courses = db.execute("""
            SELECT enrolled.course_id, courses.title, courses.card_description, courses.course_img
            FROM enrolled
            JOIN courses ON enrolled.course_id = courses.id
            WHERE enrolled.course_id = ?
        """, session["user_id"])

        return render_template("my_learning.html", my_courses=my_courses)


@app.route("/grades", methods=["GET", "POST"])
@login_required
def grades():
    # List of students who are studying the selected subject
    if request.method == "POST":
        # Getting the grade provided by a teacher
        grade = request.form.get("grade")
        id_student = request.form.get("id_student")
        id_subject = session.get("selected_subject")

        if not id_student or not grade:
            return apology("incomplete data error", 400)
        
        if int(grade) >= 0 or int(grade) <= 10:
            db.execute("""
                UPDATE grades SET grade = ?, teacher_id = ?, date = ? 
                WHERE student_id = ?
                AND subject_id = ?
            """, int(grade), session["user_id"], obtener_fecha_venezuela(), id_student, id_subject)
        else:
            return apology("wrong data error", 400)

        return redirect("/grades")
    
    else:  
        # List of students
        list_students = db.execute("""
            SELECT students.id, students.names, students.last_names, grades.grade
            FROM studying
            JOIN grades ON studying.student_id = grades.student_id AND studying.subject_id = grades.subject_id
            JOIN students ON studying.student_id = students.id
            WHERE studying.subject_id = ?
        """, session.get("selected_subject"))

        subject_name = db.execute("""
            SELECT name FROM subjects WHERE id = ?
        """, session.get("selected_subject"))

        return render_template("grades.html", list_students=list_students, subject_name=subject_name)
    

@app.route("/strategies_grades", methods=["GET", "POST"])
@login_required
def strategies_grades():
    # Changing a specific strategy grade
    if request.method == "POST":
        # Getting the strategy's grade provided by a teacher
        grade = request.form.get("grade")
        student_id = request.form.get("student_id")
        strtgy_id = request.form.get("strategy_id")

        if not student_id or not grade:
            return apology("incomplete data error", 400)
        
        if int(grade) >= 0 or int(grade) <= 10:
            db.execute("""
                UPDATE evaluated SET grade = ?
                WHERE strategy_id = ?
                AND student_id = ?
            """, int(grade), strtgy_id, student_id)
        else:
            return apology("wrong data error", 400)

        return redirect(url_for("strategies_grades"))
    
    else:  
        strategy_id = request.args.get("strategy_id")
        if strategy_id:
            session["strategy_id"] = strategy_id
        else:
            strategy_id = session.get("strategy_id")

        # List of students who must take this strategy
        list_students = db.execute("""
            SELECT evaluated.strategy_id, evaluated.student_id, students.names, students.last_names, evaluated.grade
            FROM evaluated
            JOIN students ON evaluated.student_id = students.id
            WHERE evaluated.strategy_id = ?
        """, session.get("strategy_id"))

        strategy_selected = db.execute("""
            SELECT type, topic, percentage, date
            FROM strategies
            WHERE id = ?
        """, session.get("strategy_id"))

        return render_template("strategies_grades.html", list_students=list_students, strategy_selected=strategy_selected)


@app.route("/student")
@login_required
def student():
    # Student main page
    subjects = db.execute("""
        SELECT subjects.name, subjects.semester, subjects.credits, grades.grade, teachers.names, teachers.last_names
        FROM studying
        JOIN subjects ON studying.subject_id = subjects.id
        JOIN grades ON studying.student_id = grades.student_id AND studying.subject_id = grades.subject_id
        JOIN teaching ON studying.subject_id = teaching.subject_id
        JOIN teachers ON teaching.teacher_id = teachers.id
        WHERE studying.student_id = ?
    """, session["user_id"])

    learner = db.execute("""
        SELECT names, last_names FROM students WHERE id = ?
    """, session["user_id"])

    return render_template("student.html", subjects=subjects, learner=learner)


@app.route("/add_subjects", methods=["GET", "POST"])
@login_required
def add_subjects():
    if request.method == "POST":

        adding = request.form.get("selected")

        # Checking if there's a teacher teaching that subject
        teaching = db.execute("""
            SELECT teacher_id
            FROM teaching
            WHERE subject_id = ?     
        """, adding)

        # Checking if student already enrolled the subject
        subjects = db.execute("""
            SELECT subject_id
            FROM studying
            WHERE student_id = ?
            AND subject_id = ?
        """, session["user_id"], adding)

        if len(teaching) == 0:
            return apology("there's no teacher yet", 400)
        elif len(subjects) == 1:
            return apology("registered subject", 400)
        else:
            db.execute("""
                INSERT INTO studying (student_id, subject_id) VALUES (?, ?)
            """, session["user_id"], adding)

            db.execute("""
                INSERT INTO grades (student_id, subject_id, grade, teacher_id) VALUES (?, ?, ?, ?)
            """, session["user_id"], adding, 0, teaching[0]["teacher_id"])
            
            flash("Subject added!", "success")
            return redirect("/student")
    
    else:   
            
        subjects_available = db.execute("""
            SELECT subjects.id, subjects.name, subjects.semester, subjects.credits
            FROM subjects
            JOIN students ON subjects.department_id = students.department_id
            WHERE students.id = ?
        """, session["user_id"])

        return render_template("add_subjects.html", subjects_available=subjects_available)






@app.route("/edit_pass", methods=["GET", "POST"])
@login_required
def edit_pass():
    if request.method == "POST":
        old = request.form.get("old_password")
        new = request.form.get("new_password")
        again = request.form.get("new_pass_again")

        if not old or not new or not again:
            return apology("all fields need to be filled", 400)


        if session["role"] == "student":
            update = db.execute("SELECT pw FROM students WHERE id = ?", session["user_id"])
            print(update)
            if check_password_hash(update[0]['pw'], old):
                if new == again:
                    new = generate_password_hash(again, method='scrypt', salt_length=16)
                    db.execute("UPDATE students SET pw = ? WHERE id = ?", new, session["user_id"])
                else:
                    return apology("both passwords don't match", 400)
            else:
                return apology("incorrect password", 403)
            
            flash('Password changed!', 'success')
            return redirect('/student')
            
        elif session["role"] == "teacher":
            update = db.execute("SELECT pw FROM teachers WHERE id = ?", session["user_id"])

            if check_password_hash(update[0]['pw'], old):
                if new == again:
                    new = generate_password_hash(again, method='scrypt', salt_length=16)
                    db.execute("UPDATE teachers SET pw = ? WHERE id = ?", new, session["user_id"])
                else:
                    return apology("both passwords don't match", 400)
            else:
                return apology("incorrect password", 403)
            
            flash('Password changed!', 'success')
            return redirect('/')

    else:
        return render_template("edit_pass.html")


@app.route("/settings")
@login_required
def settings():
    return render_template("settings.html")
