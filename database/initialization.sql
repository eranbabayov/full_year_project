CREATE DATABASE SecurityPerformance;
GO

USE SecurityPerformance;
GO

CREATE TABLE users (
    userID INT IDENTITY(1,1) PRIMARY KEY,
    username VARCHAR(50),
    password VARCHAR(200),
    email VARCHAR(100) UNIQUE,
    reset_token VARCHAR(200)
);
GO

CREATE TABLE user_info (
    userID INT PRIMARY KEY,
    salt VARCHAR(64),
    FOREIGN KEY (userID) REFERENCES users(userID)
);
GO


CREATE TABLE Challenges (
    challengeID INT,
    category NVARCHAR(255),
    text NVARCHAR(MAX),
    problematic_row NVARCHAR(255),
    explanation NVARCHAR(MAX),
)
GO
CREATE TABLE Solutions (
    solutionID INT,
    challengeID INT,
    text NVARCHAR(MAX),
    correctness NVARCHAR(255),
    explanation NVARCHAR(MAX),
)
GO

CREATE TABLE user_scores (
    userID INT PRIMARY KEY,
    FOREIGN KEY (userID) REFERENCES users(userID)
);
GO

CREATE TABLE password_history (
    historyID INT IDENTITY(1,1) PRIMARY KEY,
    userID INT,
    password VARCHAR(200),
    salt VARCHAR(64),
    FOREIGN KEY (userID) REFERENCES users(userID)
);
GO

CREATE TABLE category1_scores (
    userID INT PRIMARY KEY,
    score1 INT,
    score2 INT,
    score3 INT,
    score4 INT,
    score5 INT,
    FOREIGN KEY (userID) REFERENCES user_scores(userID)
);
GO

CREATE TABLE category2_scores (
    userID INT PRIMARY KEY,
    score1 INT,
    score2 INT,
    score3 INT,
    score4 INT,
    score5 INT,
    FOREIGN KEY (userID) REFERENCES user_scores(userID)
);
GO

CREATE TABLE category3_scores (
    userID INT PRIMARY KEY,
    score1 INT,
    score2 INT,
    score3 INT,
    score4 INT,
    score5 INT,
    FOREIGN KEY (userID) REFERENCES user_scores(userID)
);
GO

CREATE TABLE category4_scores (
    userID INT PRIMARY KEY,
    score1 INT,
    score2 INT,
    score3 INT,
    score4 INT,
    score5 INT,
    FOREIGN KEY (userID) REFERENCES user_scores(userID)
);
GO

CREATE TABLE category5_scores (
    userID INT PRIMARY KEY,
    score1 INT,
    score2 INT,
    score3 INT,
    score4 INT,
    score5 INT,
    FOREIGN KEY (userID) REFERENCES user_scores(userID)
);
GO

CREATE TABLE last_games_grade (
    userID INT PRIMARY KEY,
    score1 INT,
    score2 INT,
    score3 INT,
    score4 INT,
    score5 INT,
    FOREIGN KEY (userID) REFERENCES user_scores(userID)
);
GO
