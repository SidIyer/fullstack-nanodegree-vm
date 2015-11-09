-- This file is to be used to set up the schema for
-- our tournaments project.

-- Drop the database if it exists already (remember, this is for schema setup,
-- so we always start with a clean slate).
DROP DATABASE IF EXISTS tournament;

-- Create the database
CREATE DATABASE tournament;

-- Connect to the database
\connect tournament

-- Create tables
CREATE TABLE players (
	playerId BIGSERIAL UNIQUE PRIMARY KEY NOT NULL,
	fullPlayerName VARCHAR (100) NOT NULL
);

CREATE TABLE matches (
	matchId BIGSERIAL UNIQUE PRIMARY KEY NOT NULL,
	winnerId BIGINT NOT NULL REFERENCES players (playerId),
	loserId BIGINT NOT NULL REFERENCES players (playerId)
);

CREATE TABLE standings (
	playerId BIGINT UNIQUE PRIMARY KEY NOT NULL REFERENCES players (playerId),
	numberOfWins INT NOT NULL,
	numberOfLosses INT NOT NULL
);

\d
