CREATE DATABASE notehive;

USE notehive;

-- Users table
CREATE TABLE Users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role ENUM('student','teacher') NOT NULL
);

-- Faculty table
CREATE TABLE Faculty (
    faculty_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT UNIQUE,
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
);


-- Semester table
CREATE TABLE Semester (
    semester_id INT PRIMARY KEY
);

-- Subject table
CREATE TABLE Subject (
    subject_id INT AUTO_INCREMENT PRIMARY KEY,
    subject_name VARCHAR(100) NOT NULL,
    semester_id INT NOT NULL,
    FOREIGN KEY (semester_id) REFERENCES Semester(semester_id)
);



-- Notes table
CREATE TABLE Notes (
    note_id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    file_path VARCHAR(500),
    subject_id INT,
    uploaded_by INT,
    upload_date DATE,
    FOREIGN KEY (subject_id) REFERENCES Subject(subject_id),
    FOREIGN KEY (uploaded_by) REFERENCES Users(user_id)
);


-- Comments table
CREATE TABLE Comments (
    comment_id INT AUTO_INCREMENT PRIMARY KEY,
    note_id INT,
    user_id INT,
    comment_text TEXT,
    date_posted DATE,
    FOREIGN KEY (note_id) REFERENCES Notes(note_id),
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
);