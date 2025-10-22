CREATE DATABASE notehive;

USE notehive;

-- Users table
CREATE TABLE User (
    user_id INT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role ENUM('student','teacher') NOT NULL
);


-- Faculty table
CREATE TABLE Faculty (
    user_id INT UNIQUE,
    FOREIGN KEY (user_id) REFERENCES User(user_id) ON DELETE CASCADE
);


-- Semester table
CREATE TABLE Semester (
    semester_id INT PRIMARY KEY
);

-- Subject table
CREATE TABLE Subject (
    subject_id INT  PRIMARY KEY,
    subject_name VARCHAR(100) NOT NULL,
    semester_id INT,
    FOREIGN KEY (semester_id) REFERENCES Semester(semester_id) ON DELETE SET NULL
);



-- Notes table
CREATE TABLE Note (
    note_id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    file_path VARCHAR(500),
    subject_id INT,
    uploaded_by INT,
    upload_date DATE,
    FOREIGN KEY (subject_id) REFERENCES Subject(subject_id) ON DELETE SET NULL,
    FOREIGN KEY (uploaded_by) REFERENCES User(user_id) ON DELETE SET NULL
);

