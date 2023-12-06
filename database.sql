CREATE TABLE IF NOT EXISTS pokemon_stats (
	ind INT,
    Name VARCHAR(255),
    Type1 VARCHAR(255),
    Type2 VARCHAR(255),
    Total INT,
    HP INT,
    Attack INT,
    Defense INT,
    Sp_Atk INT,
    Sp_Def INT,
    Speed INT,
    Generation INT,
    Legendary BOOLEAN
);
LOAD DATA LOCAL INFILE 'C://Users//Pokeman'
INTO TABLE pokemon_stats
FIELDS TERMINATED BY ','
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;  -- This ignores the header row