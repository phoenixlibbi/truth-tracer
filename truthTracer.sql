 -- show databases;
create database truthTracer;

use truthTracer;

CREATE TABLE admin (
    admin_id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL -- You should hash passwords for security
);


CREATE TABLE user (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL -- You should hash passwords for security
);

CREATE TABLE user_detail (
    user_detail_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL,
    interaction_date VARCHAR(100) NOT NULL,
    interaction_time VARCHAR(100) NOT NULL,
    address VARCHAR(255),
    code VARCHAR(50),
    isAdmin BOOLEAN,
    html_content text,
    requested BOOLEAN,
    results TEXT,
    video LONGBLOB,
    positive TEXT,
    negative TEXT
);