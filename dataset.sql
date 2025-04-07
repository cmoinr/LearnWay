-- Insert data into the courses table
INSERT INTO courses (title, card_description, preview_description, course_img) VALUES
('Introduction to Python', 'Learn Python from scratch.', 'This course covers the basics of Python programming, including syntax, data types, control structures, functions, and more. Perfect for beginners looking to start their programming journey.', 'https://www.muycomputer.com/wp-content/uploads/2017/07/lenguaje-de-programaci%C3%B3n-1.jpg'),
('Web Development with HTML & CSS', 'Build stunning websites.', 'This course teaches you how to create beautiful and responsive websites using HTML and CSS. Learn about layouts, styling, and best practices for modern web development.', 'https://www.masterseosem.com/images/etiquetas-html.webp');

-- Insert data into the modules table
INSERT INTO modules (course_id, order_course, module_title, info) VALUES
-- Modules for Course 1: Introduction to Python
(1, 1, 'Getting Started with Python', 'Learn how to set up your Python environment, write your first Python program, and understand the basics of Python syntax.'),
(1, 2, 'Data Types and Variables', 'Explore Python data types such as integers, floats, strings, and booleans. Learn how to declare and use variables effectively.'),
(1, 3, 'Control Structures', 'Understand how to use if-else statements, loops, and other control structures to create dynamic and interactive programs.'),
(1, 4, 'Functions and Modules', 'Learn how to write reusable code using functions and organize your programs with modules.'),
(1, 5, 'Working with Files', 'Discover how to read from and write to files in Python, and learn about file handling best practices.'),

-- Modules for Course 2: Web Development with HTML & CSS
(2, 1, 'Introduction to HTML', 'Learn the basics of HTML, including how to structure a webpage with elements like headings, paragraphs, and lists.'),
(2, 2, 'Styling with CSS', 'Understand how to use CSS to style your HTML elements, including colors, fonts, and layouts.'),
(2, 3, 'Responsive Design', 'Learn how to create responsive websites that look great on all devices using media queries and flexible layouts.'),
(2, 4, 'Advanced CSS Techniques', 'Explore advanced CSS features like animations, transitions, and pseudo-classes to enhance your website.'),
(2, 5, 'Building a Complete Website', 'Combine your HTML and CSS knowledge to build a fully functional and visually appealing website.');