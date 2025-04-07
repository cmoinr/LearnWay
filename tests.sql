-- SELECT s.id, s.name, d.field, s.semester, COUNT(studying.student_id) AS 'enrolled'
-- FROM subjects s
-- JOIN departments d ON s.department_id = d.id
-- JOIN teaching t ON s.id = t.subject_id
-- JOIN teachers ts ON t.teacher_id = ts.id
-- JOIN studying ON s.id = studying.subject_id
-- WHERE t.teacher_id = ?
-- GROUP BY s.id;

-- SELECT id, names, surnames, semester FROM students
-- JOIN studying ON students.id = studying.id_student
-- WHERE studying.id_subject = ?

-- SELECT students.id, students.names, students.surnames, grades.grade
-- FROM students
-- JOIN studying ON students.id = studying.id_student
-- JOIN grades ON studying.id_subject = grades.id_subject
-- WHERE studying.id_subject = 'MA101'

-- SELECT subjects.name, subjects.semester, subjects.credits, grades.grade, teachers.names, teachers.surnames
-- FROM subjects
-- JOIN grades ON subjects.id = grades.id_subject
-- JOIN studying ON grades.id_student = studying.id_student
-- JOIN teaching ON subjects.id = teaching.id_subject
-- JOIN teachers ON teaching.id_teacher = teachers.id
-- WHERE studying.id_student = 25000100

-- SELECT subjects.name, subjects.semester, subjects.credits, grades.grade, teachers.names, teachers.surnames
-- FROM studying
-- JOIN students ON studying.id_student = students.id
-- JOIN grades ON studying.id_subject = grades.id_subject
-- JOIN subjects ON studying.id_subject = subjects.id
-- JOIN teaching ON studying.id_subject = teaching.id_subject
-- JOIN teachers ON teaching.id_teacher = teachers.id
-- WHERE studying.id_student = 25000100

-- DELETE FROM teaching
-- WHERE id_teacher = 23500120;

-- INSERT INTO grades(student_id, subject_id, teacher_id, grade)
-- VALUES ('22020202', 'SE70', '4857673', 7);

-- SELECT s.id, s.names, s.last_names, grades.grade
-- FROM students s
-- JOIN studying ON s.id = studying.student_id
-- JOIN grades ON studying.subject_id = grades.subject_id
-- WHERE studying.subject_id = 'MA001';

-- SELECT subjects.name, subjects.semester, subjects.credits, grades.grade, teachers.names, teachers.last_names
-- FROM studying
-- JOIN subjects ON studying.subject_id = subjects.id
-- JOIN grades ON studying.student_id = grades.student_id AND studying.subject_id = grades.subject_id
-- JOIN teaching ON studying.subject_id = teaching.subject_id
-- JOIN teachers ON teaching.teacher_id = teachers.id
-- WHERE studying.student_id = ?

-- ALTER TABLE evaluated
-- ADD COLUMN grade INTEGER;

-- ALTER TABLE studying, teaching
-- ADD COLUMN section TEXT;

-- INSERT INTO evaluated (strategy_id, student_id)
-- SELECT 5, students.id
-- FROM studying
-- JOIN grades ON studying.student_id = grades.student_id AND studying.subject_id = grades.subject_id
-- JOIN students ON studying.student_id = students.id
-- WHERE studying.subject_id = 'LM002'

-- SELECT evaluated.student_id, students.names, students.last_names, evaluated.grade
-- FROM evaluated
-- JOIN students ON evaluated.student_id = students.id
-- WHERE evaluated.strategy_id = ?

-- UPDATE courses
-- SET course_img = 'https://www.masterseosem.com/images/etiquetas-html.webp'
-- WHERE id = 2;

-- DROP TABLE comments;

CREATE TABLE comments (
    id INTEGER,
    user_id INTEGER NOT NULL,
    course_id INTEGER NOT NULL,
    comment TEXT NOT NULL,
    rating INTEGER NOT NULL,
    PRIMARY KEY(id)
    FOREIGN KEY(user_id) REFERENCES users(id)
    FOREIGN KEY(course_id) REFERENCES courses(id)
);