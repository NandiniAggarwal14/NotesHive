USE notehive;

INSERT INTO User (user_id, name, email, password, role) VALUES
(2314,'Nandini', 'nands@geu.ac.in', '123nands', 'student'),
(2311,'Kriti', 'kriti@geu.ac.in', '321krits', 'student'),
(20001,'Dr. Singh', 'singh@geu.ac.in', 'tsingh1', 'teacher'),
(20012,'Ms. Joshi', 'joshi@geu.ac.in', 'joshit2', 'teacher');

INSERT INTO Faculty (user_id) VALUES
(20001), 		 -- Dr. Singh
(20012); 		 -- Ms. Joshi

INSERT INTO Semester (semester_id) VALUES
(1),
(2),
(3),
(4),
(5),
(6);

INSERT INTO Subject (subject_id, subject_name, semester_id) VALUES
(210,'DBMS', 2),
(134,'Data Structures', 1),
(306,'Operating Systems', 3),
(411,'Computer Networks', 4),
(219,'AI Basics', 2);

INSERT INTO Note (title, description, file_path, subject_id, uploaded_by, upload_date) VALUES
('DBMS Proposal', 'Creating a website for note sharing', 'https://drive.google.com/file/d/1ViYZctrC_JxuIU0zmnqSsYppc3JUY2Ci/view?usp=sharing', 210, 20001, '2025-10-05'),
('AI Basics', 'Introduction to AI', 'https://drive.google.com/file/d/1YVBphvsl2u3zaLFZzdDSPJevSZgXWRkV/view?usp=drive_link', 219, 2311, '2025-09-16'),
('Linked Lists', 'Notes on singly & doubly linked lists', 'https://drive.google.com/file/d/ghi789/view', 134, 20001, '2025-10-01'),
('OS Presentation', 'Firewall Demonstration', 'https://docs.google.com/presentation/d/1osq5apb7_Ki0AFuBntbIPFWIRWlo_UwU/edit?usp=sharing&ouid=103908473392938725216&rtpof=true&sd=true', 306, 20012, '2025-10-06');

