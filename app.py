import os, re, datetime, pytz

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, url_for, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import login_required

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
            flash("Todos los campos deben estar llenos.", 'error')
            return render_template("register.html", names=names, surnames=surnames, email=email, password=password, confirmation=confirmation)
        
        if not re.match(r"^[a-zA-Z]+$", names) or not re.match(r"^[a-zA-Z]+$", surnames):
            flash("Nombres o apellidos inválidos.", 'error')
            return render_template("register.html", names=names, surnames=surnames, email=email, password=password, confirmation=confirmation)
        
        if password == confirmation:
            password = generate_password_hash(confirmation, method='scrypt', salt_length=16)            
        else:
            flash("Ambas contraseñas no coinciden.", 'error')
            return render_template("register.html", names=names, surnames=surnames, email=email, password=password, confirmation=confirmation)
        
        try:
            db.execute("""
                INSERT INTO users (names, surnames, email, hash, profile_img)
                VALUES(?, ?, ?, ?, ?)
            """, names, surnames, email, password, default_profile)     
            flash("Has sido registrado exitosamente!", 'success')
            return redirect("/login")       
        except ValueError:
            flash("Ya te encuentras registrado. Inicia sesión!", 'error')
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
            flash("Todos los campos deben estar llenos.", 'error')
            return render_template("login.html", email=email, password=password)

        # Query database for credentials
        user = db.execute("SELECT id, names, surnames, hash, profile_img FROM users WHERE email = ?", email)

        # Ensure username exists and password is correct
        if len(user) != 1 or not check_password_hash(user[0]["hash"], password):
            flash("Contraseña o email inválidos.", 'error')
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
            flash("Todos los campos deben estar llenos.", "error")
            return redirect(f"/course_preview/{course_id}")

        # Insertar la reseña en la base de datos
        db.execute("""
            INSERT INTO comments (user_id, course_id, comment, rating)
            VALUES (?, ?, ?, ?)
        """, session["user_id"], course_id_form, comment, int(rating))

        flash("Reseña enviada exitosamente!", "success")
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
            flash("Curso no encontrado.", "error")
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


@app.route("/profile_settings", methods=['GET', 'POST'])
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
            WHERE enrolled.user_id = ?
        """, session["user_id"])

        return render_template("my_learning.html", my_courses=my_courses)


@app.route("/enroll/<int:course_id>", methods=['GET'])
@login_required
def enroll(course_id):
    user_id = session["user_id"]

    # Verificar si el curso existe
    course = db.execute("SELECT id FROM courses WHERE id = ?", course_id)
    if len(course) == 0:
        flash("El curso no existe.", "danger")
        return redirect(url_for('index'))

    # Verificar si el usuario ya está inscrito
    enrollment = db.execute(
        "SELECT user_id FROM enrolled WHERE user_id = ? AND course_id = ?", user_id, course_id
    )
    if len(enrollment) >= 1:
        flash("Ya estás inscrito en este curso.", "info")
        return redirect(url_for('course_preview', course_id=course_id))

    # Insertar el registro en la tabla "enrolled"
    db.execute(
        "INSERT INTO enrolled (user_id, course_id, enrollment_date) VALUES (?, ?, ?)",
        user_id, course_id, obtener_fecha_venezuela()
    )

    flash("Te has inscrito exitosamente en el curso.", "success")
    return redirect(url_for('course_preview', course_id=course_id))

