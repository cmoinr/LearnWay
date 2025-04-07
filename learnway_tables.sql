CREATE TABLE users (
    id INTEGER,
    names TEXT NOT NULL,
    surnames TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    hash TEXT NOT NULL,
    profile_img TEXT,
    PRIMARY KEY(id)
);

CREATE TABLE courses (
    id INTEGER,
    title TEXT NOT NULL,
    card_description TEXT NOT NULL,
    preview_description TEXT NOT NULL,
    course_picture BLOB,
    PRIMARY KEY(id)
);

CREATE TABLE modules (
    id INTEGER,
    course_id INTEGER NOT NULL,
    order_course INTEGER NOT NULL,
    module_title TEXT NOT NULL,
    info TEXT NOT NULL,
    PRIMARY KEY(id)
    FOREIGN KEY(course_id) REFERENCES courses(id)
);

CREATE TABLE comments (
    id INTEGER,
    user_id INTEGER NOT NULL,
    course_id INTEGER NOT NULL,
    comment TEXT NOT NULL,
    rating INTEGER NOT NULL,
    FOREIGN KEY(user_id) REFERENCES users(id)
    FOREIGN KEY(course_id) REFERENCES courses(id)
);

CREATE TABLE enrolled (
    user_id INTEGER NOT NULL,
    course_id INTEGER NOT NULL,
    PRIMARY KEY(user_id, course_id)
    FOREIGN KEY(user_id) REFERENCES users(id)
    FOREIGN KEY(course_id) REFERENCES courses(id)
);