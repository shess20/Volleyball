--Cassie Richter
create database liberty_league_volleyball;
grant all privileges on database  liberty_league_volleyball to ehar;

--When I read in the CSV's they made the tables automatically while
-- also inserting the data, so I will show what the create table commands would be
-- but, I did not have the use create table
-- I imported my csvs, and then manually added in the primary and foreign keys for each table.

-- I wil put the DDL for each table commented (since they weren't run, they just get created on import)

-- TEAMS
/*
create table teams
(
    school   varchar not null,
    conf_wins      integer,
    conf_losses    integer,
    overall_wins   integer,
    overall_losses integer,
    year           integer,
    league         varchar
);
*/
-- Then, I added the primary key of this table
alter table teams add primary key (school);

-- MATCHES

/*
create table matches (
    home       varchar,
    away       varchar,
    matchwin   varchar,
    date       date,
    time       time,
    site       varchar,
    attendance integer,
    url        varchar not null
);
 */
-- Primary and foreign keys for matches
alter table matches add primary key (url);
alter table matches add foreign key (home) references teams(school);
alter table matches add foreign key (away) references teams(school);

-- PLAYERS
/*
 create table players (
    last_name  varchar not null,
    first_name varchar not null,
    number     integer not null,
    school     varchar not null,
);
 */
--primary and foreign keys for players
alter table players add primary key (last_name,first_name, school,number);
alter table players add foreign key (school) references teams(school);

-- PLAYERSTATS
/*
create table playerstats (
    school     varchar not null,
    number     integer,
    last_name  varchar not null,
    first_name varchar not null,
    sp         integer,
    k          integer,
    e          integer,
    ta         integer,
    pct        numeric,
    a          integer,
    sa         integer,
    se         integer,
    bs         integer,
    ba         integer,
    be         integer,
    dig        integer,
    bhe        integer,
    re         integer,
    pts        numeric,
    h_a        varchar,
    url        varchar not null
);
*/

alter table playerstats add primary key (last_name,first_name, school,url);

alter table playerstats
    add foreign key (last_name,first_name, school,number) references players(last_name,first_name, school,number);
alter table playerstats
    add foreign key (url) references matches(url);


--SETS
/*
 create table sets (
    school     varchar not null,
    set        integer not null,
    points     integer,
    url        varchar not null,
    point_diff integer,
    set_winner varchar,
    k          integer,
    e          integer,
    ta         integer,
    "%"        numeric
 );
 */

alter table sets add primary key (school,set,url);
alter table sets add foreign key (url) references matches(url);

-- This database is for analysis/viewing, not for a user to input data
-- so a user will not need an update/insert commands

-- SQL Queries (All in Python as well) For Analysis
-- all regression also looked further into in the R file


-- If a user wants to preview the data tables to see the attribute names and structure before running analytics
-- Example for matches, but as shown in python can be for any table
 SELECT
     *
FROM
    matches
LIMIT
    5;


-- To look at the records of all liberty league teams
-- If DB expanded, this could be applied to any League desired to look at
SELECT
    *
FROM
    teams
WHERE
    league = 'LibertyLeague';

-- Run Regressions
-- First example is between Attendance and Points
-- Run for home or away options
SELECT
    REGR_SLOPE(t.points,attendance) SLOPE,
    REGR_INTERCEPT(t.points,attendance) INTCPT,
    REGR_R2(t.points,attendance) RSQR,
    REGR_COUNT(t.points,attendance) COUNT,
    REGR_AVGX(t.points,attendance) avgattendance,
    REGR_AVGY(t.points,attendance) avgpoints
FROM
    matches natural join sets as t
where
    home = t.school
group by
    t.set;


--Basic analytic query for stats based on teams winnning or losing the individual set and overall match
select
    avg(t.k) as average_kills, avg(t.e) as average_errors, avg(t."%") as avg_pct
FROM
    matches natural join sets as t
where
    matchwin = t.school AND t.set_winner = t.school
group by
    t.set;

-- Basic Stats for a given team
select
    avg(overall_wins) as overall_wins, avg(overall_losses) as overall_losses, avg(s.k) as avg_kills,
     avg(s.e) as avg_errors, avg(s."%") as avg_pct, school
from
    teams natural join sets as s
where
    school = 'St. Lawrence'
group by
    school;

--Run a Regression on Aces and Points
with aces as (select
                    sum(sa) as aces, url, school
                from playerstats
                group by url, school),
    points as (select sum(points) as points, url, school
               from sets
               group by url, school)
select REGR_SLOPE(points, aces) SLOPE,
  REGR_INTERCEPT(points, aces) INTCPT,
  REGR_R2(points, aces) RSQR,
  REGR_COUNT(points, aces) COUNT,
  REGR_AVGX(points, aces) avg_aces,
  REGR_AVGY(points, aces) avg_points
from aces natural join points;


-- Basic Stats for a Teams Roster
-- Could be changed for any desired stats and team
select
    last_name, first_name, avg(a) as avg_assists,avg(dig) as avg_sigs, avg(pts) as avg_points
from
    playerstats
where
    lower(school) = 'St. Lawrence'
group by
    last_name, first_name;


-- Stats avg per match over all players
-- Can get just top 20 or how ever many you want to see
-- Can also be done for any stats
with avgpts as
            (select avg(p.pts) as avg, school, p.last_name, p.first_name
            from playerstats as p
            group by school, p.last_name, p.first_name)
select
    max(a.avg) avg_points, a.school, a.last_name, a.first_name
from
    avgpts as a
group by
    a.school, a.last_name, a.first_name
order by
    max(a.avg) desc
limit 20;

-- Gets any statistic from players and gets the top 10
-- This is for Season totals
 select
    sum(k) as total, school, last_name, first_name
from
    playerstats
group by
    school, last_name, first_name
order by
    total desc
limit
    10;


-- gets kills over time regression for an inputted last name and schoool
-- example player last name with school
        -- Ehnstrom,  Vassar
        -- Piper, St. Lawrence
        -- Werdine, Clarkson
--Date converted to days since season started in order to regress
WITH days as (
            SELECT date - '2021-09-01' AS days, m.k as kills, m.last_name as last_name, school
            FROM matches natural join playerstats as m
            )
SELECT
    REGR_SLOPE(kills, days) SLOPE,
    REGR_INTERCEPT(kills, days ) INTCPT,
    REGR_R2(kills, days ) RSQR,
    REGR_COUNT(kills, days) COUNT,
    REGR_AVGY(kills, days ) AVGKills
FROM
    days
where
    lower(last_name) = 'Piper' and lower(school) = 'St. Lawrence';



-- These are all just examples and there are many variations of these that can be done
-- There is also many new regression and stats that could be analyzed.