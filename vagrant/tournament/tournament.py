#!/usr/bin/env python
# 
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2


def connect():
    # Connect to the PostgreSQL database.  Returns a database connection.
    return psycopg2.connect("dbname=tournament")


def deleteMatches():
    # Remove all the match records from the database.
    conn = connect();
    cur  = conn.cursor();
    cur.execute("DELETE FROM matches");
    conn.commit();
    cur.close();
    conn.close();


def deletePlayers():
    # Remove all the player records from the database.
    conn = connect();
    cur  = conn.cursor();

    """
    Standings contains references to playerId in players,
    so delete records in standings first
    """
    cur.execute("DELETE FROM standings");
    cur.execute("DELETE FROM players");
    conn.commit();
    cur.close();
    conn.close();


def countPlayers():
    # Returns the number of players currently registered.
    conn = connect();
    cur  = conn.cursor();
    cur.execute("SELECT COUNT(*) FROM players");
    result = cur.fetchone();
    rowCount = result[0];
    conn.commit();
    cur.close();
    conn.close();
    return rowCount;


def registerPlayer(name):
    """
    Adds a player to the tournament database.
  
    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)
  
    Args:
      name: the player's full name (need not be unique).
    """
    # Clean up the name
    name = name.replace("'", "''")

    conn = connect();
    cur  = conn.cursor();

    sql = "INSERT INTO players (fullPlayerName) VALUES ('%s') RETURNING playerId" %name;
    cur.execute(sql);
    addedPlayerRow = cur.fetchone();
    addedPlayerId = addedPlayerRow[0];

    """
    Every time we register a new player, we need to create a fresh record
    for this player's standings
    """
    sql = "INSERT INTO standings (playerId, numberOfWins, numberOfLosses) VALUES (%d,0,0)" %addedPlayerId;
    cur.execute(sql);
    conn.commit();
    cur.close();
    conn.close();


def playerStandings():
    """
    Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place, or a player
    tied for first place if there is currently a tie.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """
    conn = connect();
    cur  = conn.cursor();
    sql = """   SELECT 
                    players.playerId, 
                    players.fullPlayerName,
                    standings.numberOfWins, 
                    (
                        SELECT 
                            COUNT(*) 
                                FROM (
                                        SELECT players.playerID as playerId, COUNT(*) as matchCount
                                        FROM players 
                                        INNER JOIN matches ON (playerId = matches.winnerId OR playerId = matches.loserId)
                                        GROUP BY playerId
                                    ) playerMatches 
                        WHERE players.playerId = playerMatches.playerId)
                FROM players, standings
                WHERE players.playerId = standings.playerId""";
    cur.execute(sql);
    results = cur.fetchall();
    conn.commit();
    cur.close();
    conn.close();
    return results;

def reportMatch(winner, loser):
    """
    Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
   """
    conn = connect();
    cur  = conn.cursor();

    # Record the winner and loser in the matches table
    sql = "INSERT INTO matches (winnerId, loserId) VALUES (%d, %d)" %(winner, loser)
    cur.execute(sql);

    # Update the number of wins for the winner
    sql = "SELECT numberOfWins FROM standings WHERE standings.playerId = %d" %winner;
    cur.execute(sql);
    numberOfWinnerWins = cur.fetchone()[0];
    numberOfWinnerWins = numberOfWinnerWins + 1;
    sql = "UPDATE standings SET numberOfWins = %d WHERE standings.playerId = %d" % (numberOfWinnerWins, winner);
    cur.execute(sql); 

    # Update the number of losses for the loser
    sql = "SELECT numberOfLosses FROM standings WHERE standings.playerId = %d" %loser;
    cur.execute(sql);
    numberOfLoserLosses = cur.fetchone()[0];
    numberOfLoserLosses = numberOfLoserLosses + 1;
    sql = "UPDATE standings SET numberOfLosses = %d WHERE standings.playerId = %d" % (numberOfLoserLosses, loser);
    cur.execute(sql); 

    conn.commit();
    cur.close();
    conn.close();
 
def nameForPlayerId(playerId):
    conn = connect();
    cur  = conn.cursor();
    sql = "SELECT fullPlayerName FROM players WHERE players.playerId = %d" %playerId;
    cur.execute(sql);
    playerName = cur.fetchone()[0];
    conn.commit();
    cur.close();
    conn.close();
    return playerName;
 
def swissPairings():
    """
    Returns a list of pairs of players for the next round of a match.
  
    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.
  
    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """
    conn = connect();
    cur  = conn.cursor();
    cur.execute("SELECT * FROM standings ORDER BY standings.numberOfWins DESC");
    results = cur.fetchall();

    pairings = [];

    if (len(results) > 1 and len(results) % 2 == 0):
        for i in range(0, len(results), 2):
            firstPlayerId = results[i][0];
            firstPlayerName = nameForPlayerId(firstPlayerId);
            secondPlayerId = results[i+1][0];
            secondPlayerName = nameForPlayerId(secondPlayerId);
            matchUpTuple = (firstPlayerId, firstPlayerName, secondPlayerId, secondPlayerName);
            pairings.append(matchUpTuple);
    else:
        print "Standings do not contain an adequate number of players.";

    conn.commit();
    cur.close();
    conn.close();

    return pairings;

