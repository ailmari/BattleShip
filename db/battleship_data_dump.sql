INSERT INTO "game" VALUES(12345,"2018-2-21 13:40:36.877952", "2018-2-25 13:40:36.877952", 10, 10, 5);
INSERT INTO "game" VALUES(12346,"2018-2-22 12:40:36.877952", null, 10, 10, 5);
INSERT INTO "game" VALUES(12347,"2018-2-23 12:40:36.877952", null, 12, 12, 10);

INSERT INTO "player" VALUES(1, "Fu1L_s41V0_n05CoP3_720", 12345);
INSERT INTO "player" VALUES(2, "Captain Haddock", 12345);
INSERT INTO "player" VALUES(3, "SUBMARINEGOD", 12345);

INSERT INTO "ship" VALUES(1, 1, 12345, 2, 3, 2, 6, "frigate");
INSERT INTO "ship" VALUES(2, 1, 12345, 3, 6, 6, 6, "submarine");
INSERT INTO "ship" VALUES(3, 1, 12345, 3, 6, 4, 4, "submarine");
INSERT INTO "ship" VALUES(4, 1, 12345, 9, 5, 9, 9, "carrier");

INSERT INTO "turn" VALUES(1, 1, 12345);
INSERT INTO "turn" VALUES(1, 2, 12345);
INSERT INTO "turn" VALUES(1, 3, 12345);
INSERT INTO "turn" VALUES(2, 1, 12345);
INSERT INTO "turn" VALUES(2, 2, 12345);
INSERT INTO "turn" VALUES(2, 3, 12345);

INSERT INTO "shot" VALUES(1, 1, 12345, 4, 4, "single");
INSERT INTO "shot" VALUES(1, 2, 12345, 3, 3, "single");
INSERT INTO "shot" VALUES(1, 3, 12345, 2, 3, "single");
INSERT INTO "shot" VALUES(2, 1, 12345, 5, 4, "single");
