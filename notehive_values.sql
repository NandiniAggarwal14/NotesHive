USE notehive;

INSERT INTO Users (name, email, password, role) VALUES
('Nandini', 'nands@geu.ac.in', '123nands', 'student'),
('Kriti', 'kriti@geu.ac.in', '321krits', 'student'),
('Dr. Singh', 'singh@geu.ac.in', 'tsingh1', 'teacher'),
('Mr. Joshi', 'joshi@geu.ac.in', 'joshit2', 'teacher');

INSERT INTO Faculty (user_id) VALUES
(3),  -- Dr. Smith
(4);  -- Dr. Johnson

INSERT INTO Semester (semester_id) VALUES
(1),
(2),
(3),
(4),
(5),
(6);

INSERT INTO Subject (subject_name, semester_id) VALUES
('DBMS', 2),
('Data Structures', 1),
('Operating Systems', 3),
('Computer Networks', 4),
('AI Basics', 2);

INSERT INTO Notes (title, description, file_path, subject_id, uploaded_by, upload_date) VALUES
('DBMS Proposal', 'Creating a website for note sharing', 'https://drive.google.com/file/d/1ViYZctrC_JxuIU0zmnqSsYppc3JUY2Ci/view?usp=sharing', 1, 3, '2025-10-05'),
('AI Basics', 'Introduction to AI', 'https://drive.google.com/file/d/1YVBphvsl2u3zaLFZzdDSPJevSZgXWRkV/view?usp=drive_link', 5, 2, '2025-09-16'),
('Linked Lists', 'Notes on singly & doubly linked lists', 'https://drive.google.com/file/d/ghi789/view', 2, 3, '2025-10-01'),
('OS Presentation', 'Firewall Demonstration', 'https://docs.google.com/presentation/d/1osq5apb7_Ki0AFuBntbIPFWIRWlo_UwU/edit?usp=sharing&ouid=103908473392938725216&rtpof=true&sd=true', 3, 4, '2025-10-06');

INSERT INTO Comments (note_id, user_id, comment_text, date_posted) VALUES
(1, 1, 'Can you explain semantic search again?', '2025-10-06'),
(2, 1, 'Thanks, this was helpful!', '2025-10-06'),
(3, 2, 'Good notes on linked lists!', '2025-10-06'),
(4, 1, 'This helped me understand firewall working', '2025-10-06');
