PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS game(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  start_time DATETIME,
  end_time DATETIME,
  x_size INTEGER,
  y_size INTEGER,
  turn_length INTEGER);
CREATE TABLE IF NOT EXISTS player(
  id INTEGER,
  nickname TEXT,
  game INTEGER,
  PRIMARY KEY(id, game),
  FOREIGN KEY(game) REFERENCES game(id) ON DELETE CASCADE);
CREATE TABLE IF NOT EXISTS ship(
   id INTEGER,
   player INTEGER,
   game INTEGER,
   stern_x INTEGER,
   stern_y INTEGER,
   bow_x INTEGER,
   bow_y INTEGER,
   ship_type TEXT,
   PRIMARY KEY(id, player, game),
   FOREIGN KEY(player, game) REFERENCES player(id, game) ON DELETE CASCADE);
CREATE TABLE IF NOT EXISTS turn(
   turn_number INTEGER,
   player INTEGER,
   game INTEGER,
   PRIMARY KEY(turn_number, player, game),
   FOREIGN KEY(player, game) REFERENCES player(id, game) ON DELETE CASCADE);
CREATE TABLE IF NOT EXISTS shot(
   turn INTEGER,
   player INTEGER,
   game INTEGER,
   x INTEGER,
   y INTEGER,
   shot_type TEXT,
   PRIMARY KEY(turn, player, game, x, y),
   FOREIGN KEY(turn, player, game) REFERENCES turn(turn_number, player, game) ON DELETE CASCADE);
COMMIT;
PRAGMA foreign_keys=ON;
