
from html import unescape

import psycopg2
from numpy.core.defchararray import lower
from psycopg2.extras import RealDictCursor
from tabulate import tabulate
from json import dumps

def connect_ratings():
    """
    Connect to the volleyball database and return the connection object
    Function exists the program if there is an error
    :return: connection object
    """
    # read the password file

    ##pwd = input("please enter password: ")

    ## read the password file
    try:
        pwd_file2 = open('.pwd2')  # pswd file should be in a secure location
        ##pwd = pwd_file.readline()
    except OSError:
        print("Error: No authorization")
        exit()

    # what can go wrong?

    try:
        conn = psycopg2.connect(
            dbname="liberty_league_volleyball", ## connect to LibertyLeague Database
            user="cjrich19",
            password=pwd_file2.readline(),
            host="ada.hpc.stlawu.edu"
        )
    except psycopg2.Error:
        print("Error: cannot connect to database")
        exit()

    finally:
        pwd_file2.close()

    return conn


def menu():
    """
    Present the user with a menu and return selection
    only if valid
    :return: option selected
    """
    while True:
        print("1) Get the first 5 rows of any table to see variables")
        print("2) Get Records of all Liberty League Teams")
        print("3) How does Attendance effect points scored per set for Home teams and Away teams?")
        print("4) Get stats per set based on if they won the set and or match")
        print("5) Get the overall record and Stats of a given Liberty League team ")
        print("6) Get the top 20 Players with the highest average points per game")
        print("7) Perform a regression between Service Aces and Points Scored")
        print("8) All Players Average assists, digs, and points per match given A Team")
        print('9) Get the 10 players with the highest total stats given the statistic')
        print("10) Given a Player's last name and school, get Regression Statistics on their Kills over time")
        print("11) Output a Schools roster in JSON format given a school")
        print("12) Output Liberty League Records as a JSON")

        print("Q) Quit")

        opt = input("> ")
        if opt in ['1', '2', '3','4', '5', "6","7","8","9", '10' , '11','12', 'q', 'Q']:
            break

    return opt


##Allows a user to preview any of the tables of the database
def select_tbl(conn):
    tablein = input("Enter the table you'd like to View. The options are - matches, teams, players, playerstats, sets: ")
    tablein = tablein.lower()

    if tablein == "matches":
        cmd = """
            SELECT
                *
            FROM
                matches
            LIMIT
                5
            """
        headers = ["home", "away", "match_winner", "date","time","site","attendance","url"]
    if tablein == "sets":
        cmd = """
            SELECT
                *
            FROM
                sets
            LIMIT
                5
            """
        headers = ["school", "set", "points", "url", "point_diff", "set_winner","k","e","ta", "%"]
    if tablein == "playerstats":
        cmd = """
            SELECT
                *
            FROM
                playerstats
            LIMIT
                5
            """
        headers = ["last_name", "first_name" , "number", "school" , "sp", "k", 'e', "ta", "a", 'pct', "points", "se",
                   "sa", "bs", "be", 'ba', "dig", "bhe", "re", "h_a", "url"]
    if tablein == "players":
        cmd = """
            SELECT
                *
            FROM
                players
            LIMIT
                5
            """
        headers = ["last_name", "first_name", "number", "school"]
    if tablein == "teams":
        cmd = """
            SELECT
                *
            FROM
                teams
            LIMIT
                5
            """
        headers = ["school", "conf_wins", "conf_losses", "overall_wins", "overall_losses","year", "league"]


    cur = conn.cursor()

    ## call execute and pass in as a tuple, arguments to the command string
    cur.execute(cmd)  # trailing comma to make it a tuple

    table  =[]
    for row in cur:
        table.append(row)

    print("\n")
    print(tabulate(table, tablefmt='fancy_grid', headers=headers))


## Allows user to see the records of liberty league teams
def lib_league_records(conn):

    cmd = """
        SELECT
            *
        FROM
            teams
        WHERE
            league = %s
    """
    league = "LibertyLeague"

    # a cursor is an object for issuing SQL commands to a connection
    cur = conn.cursor()

    ## call execute and pass in as a tuple, arguments to the command string
    cur.execute(cmd, (league,))  # trailing comma to make it a tuple

    table = [("School", "Conf_Wins", "Conf_Losses", "Overall_Wins","Overall_Losses", "Year", "League")]
    for row in cur:
        newrow = [unescape(str(i)) for i in row]
        table.append(newrow[0:7])
    print("\n")
    print(tabulate(table, tablefmt='fancy_grid', headers="firstrow"))


## Runs a regression on Attendance and Point Scored
## Allows user to input whether they want to look at Home teams or Away teams
def attendance_reg(conn):
    team = input("Enter home or away: ")
    if team == "Home" or team == "home":
        cmd = """
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
            """
    if team == "away" or team == "Away":
        cmd = """
                    SELECT 
                        REGR_SLOPE(t.points,attendance) SLOPE,
                        REGR_INTERCEPT(t.points,attendance) INTCPT,
                        REGR_R2(t.points,attendance) RSQR,
                        REGR_COUNT(t.points,attendance) COUNT,
                        REGR_AVGX(t.points,attendance) AVGLISTP,
                        REGR_AVGY(t.points,attendance) AVGQSOLD
                    FROM 
                        matches natural join sets as t
                    where
                        away = t.school
                    group by 
                        t.set;
                """


    # a cursor is an object for issuing SQL commands to a connection
    cur = conn.cursor()

    ## call execute and pass in as a tuple, arguments to the command string
    cur.execute(cmd)  # trailing comma to make it a tuple

    table = [("slope", "intercept", "rsq", "count", "avg_attendance", "avg_points")]
    for row in cur:
        newrow = [unescape(str(i)) for i in row]
        table.append(newrow[0:6])
    print("\n")
    print("Regression Stats for Attendance effecting points for " + team + " team, per set")
    print("\n")
    print(tabulate(table, tablefmt='fancy_grid', headers="firstrow"))



## Allows user to see statistics contingent on if teams won the set or match combination
## user inputs whether they want to look at teams that won/lost at the set level
## and another input for teams that won/lost at the match level
def set_stats_winner(conn):
    set_won = input("For stats from teams that won the set, enter true. To get teams that lost the set, enter false: ")
    set_won = set_won.lower()
    match_win = input("For stats from teams that won the MATCH, enter true. To get teams that lost the MATCH, enter false: ")
    match_win = match_win.lower()

    if set_won == "true" and match_win == "true":
        cmd = """
            select
                avg(t.k) as average_kills, avg(t.e) as average_errors, avg(t."%") as avg_pct
            FROM 
                matches natural join sets as t
            where 
                matchwin = t.school AND t.set_winner = t.school
            group by
                t.set;
            """
    if match_win == "true" and set_won == "false":
        cmd = """
                    select
                        avg(t.k) as average_kills, avg(t.e) as average_errors, avg(t."%") as avg_pct
                    FROM 
                        matches natural join sets as t
                    where 
                        matchwin = t.school AND t.set_winner != t.school
                    group by
                        t.set;
                    """
    if match_win == "false" and set_won == "false":
        cmd = """
                    select
                        avg(t.k) as average_kills, avg(t.e) as average_errors, avg(t."%") as avg_pct
                    FROM 
                        matches natural join sets as t
                    where 
                        matchwin != t.school AND t.set_winner != t.school
                    group by
                        t.set;
                    """
    if match_win == "false" and set_won == "true":
        cmd = """
                    select
                        avg(t.k) as average_kills, avg(t.e) as average_errors, avg(t."%") as avg_pct
                    FROM 
                        matches natural join sets as t
                    where 
                        matchwin != t.school AND t.set_winner = t.school
                    group by
                        t.set;
                    """


    cur = conn.cursor()

    ## call execute and pass in as a tuple, arguments to the command string
    cur.execute(cmd)  # trailing comma to make it a tuple

    table = [("avg_kills", "avg_errors", "avg_percent")]
    for row in cur:
        newrow = [unescape(str(i)) for i in row]
        table.append(newrow[0:3])
    print("\n")
    print(tabulate(table, tablefmt='fancy_grid', headers="firstrow"))


## Returns stats for a user inputted team from the liberty league
def lib_stats(conn):

    libleagueteam = input("Enter a Liberty League Team (Bard, St. Lawrence, Clarkson, RIT, Ithaca, Skidmore, Vassar, Union): ")

    cmd = """
        select 
            avg(overall_wins) as overall_wins, avg(overall_losses) as overall_losses, avg(s.k) as avg_kills,
             avg(s.e) as avg_errors, avg(s."%%") as avg_pct, school
        from 
            teams natural join sets as s
        where
            school = %s
        group by 
            school
    """
    cur = conn.cursor()

    ## call execute and pass in as a tuple, arguments to the command string
    cur.execute(cmd, (libleagueteam,))  # trailing comma to make it a tuple

    table = [("overall_wins", "overall_wins","avg_kills", "avg_errors", "avg_pct", "school")]
    for row in cur:
        newrow = [unescape(str(i)) for i in row]
        table.append(newrow[0:6])
    print("\n")
    print(tabulate(table, tablefmt='fancy_grid', headers="firstrow"))

## Run a regression on service aces effecting points
def regress_aces(conn):
    cmd = """
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
    from aces natural join points
    """
    cur = conn.cursor()

    ## call execute and pass in as a tuple, arguments to the command string
    cur.execute(cmd)
    # trailing comma to make it a tuple
    table = [("slope", "intercept", "rsqrd", "count", "avg_aces", "avg_points")]
    for row in cur:
        newrow = [unescape(str(i)) for i in row]
        table.append(newrow[0:6])
    print("\n")
    print(tabulate(table, tablefmt='fancy_grid', headers="firstrow"))


## Get a teams player's stats average for main stats
def roster_stats(conn):
    school = input("Enter a Team: ")
    school = school.lower()

    cmd = """
    select 
        last_name, first_name, avg(a) as avg_assists,avg(dig) as avg_sigs, avg(pts) as avg_points
    from 
        playerstats
    where
        lower(school) = %s
    group by 
        last_name, first_name;
    """
    cur = conn.cursor()

    ## call execute and pass in as a tuple, arguments to the command string
    cur.execute(cmd, (school,))  # trailing comma to make it a tuple

    table = [("last_name", "first_name", "avg_assists", "avg_digs", "avg_points")]
    for row in cur:
        newrow = [unescape(str(i)) for i in row]
        table.append(newrow[0:5])
    print("\n")
    print(tabulate(table, tablefmt='fancy_grid', headers="firstrow"))


## Get a the top 20 players in the data with the highest average points per game
def player_stats(conn):
    cmd = """
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
        """
    cur = conn.cursor()

    ## call execute and pass in as a tuple, arguments to the command string
    cur.execute(cmd, )  # trailing comma to make it a tuple

    table = [("avg_points", "school", "last_name", "first_name")]
    for row in cur:
        newrow = [unescape(str(i)) for i in row]
        table.append(newrow[0:4])
    print("\n")
    print(tabulate(table, tablefmt='fancy_grid', headers="firstrow"))


## Allows user to input any player stat
## gets the top 10
def player_stat10(conn):

    stat = input("Enter what statistic you'd like to check (k, e, ta, pct,a, sa,se,bs,ba,be,digs, bhe, re): ")
    stat = stat.lower()
    if stat == 'k':
        cmd = """
            
            select 
                sum(k) as total, school, last_name, first_name
            from 
                playerstats
            group by
                school, last_name, first_name
            order by 
                total desc
            limit 
                10
        """
    if stat == 'e':
        cmd = """

            select 
                sum(e) as total, school, last_name, first_name
            from 
                playerstats
            group by
                school, last_name, first_name
            order by 
                total desc
            limit 
                10
        """
    if stat == 'ta':
        cmd = """

            select 
                sum(ta) as total, school, last_name, first_name
            from 
                playerstats
            group by
                school, last_name, first_name
            order by 
                total desc
            limit 
                10
        """

    if stat == 'pct':
        cmd = """

            select 
                sum(pct) as total, school, last_name, first_name
            from 
                playerstats
            group by
                school, last_name, first_name
            order by 
                total desc
            limit 
                10
        """
    if stat == 'a':
        cmd = """

            select 
                sum(a) as total, school, last_name, first_name
            from 
                playerstats
            group by
                school, last_name, first_name
            order by 
                total desc
            limit 
                10
        """
    if stat == 'sa':
        cmd = """

            select 
                sum(sa) as total, school, last_name, first_name
            from 
                playerstats
            group by
                school, last_name, first_name
            order by 
                total desc
            limit 
                10
        """
    if stat == 'se':
        cmd = """

            select 
                sum(se) as total, school, last_name, first_name
            from 
                playerstats
            group by
                school, last_name, first_name
            order by 
                total desc
            limit 
                10
        """
    if stat == 'bs':
        cmd = """

            select 
                sum(bs) as total, school, last_name, first_name
            from 
                playerstats
            group by
                school, last_name, first_name
            order by 
                total desc
            limit 
                10
        """
    if stat == 'ba':
        cmd = """

            select 
                sum(ba) as total, school, last_name, first_name
            from 
                playerstats
            group by
                school, last_name, first_name
            order by 
                total desc
            limit 
                10
        """
    if stat == 'be':
        cmd = """

            select 
                sum(be) as total, school, last_name, first_name
            from 
                playerstats
            group by
                school, last_name, first_name
            order by 
                total desc
            limit 
                10
        """
    if stat == 'digs' or stat == 'dig':
        cmd = """

            select 
                sum(dig) as total, school, last_name, first_name
            from 
                playerstats
            group by
                school, last_name, first_name
            order by 
                total desc
            limit 
                10
        """
    if stat == 'bhe':
        cmd = """

            select 
                sum(bhe) as total, school, last_name, first_name
            from 
                playerstats
            group by
                school, last_name, first_name
            order by 
                total desc
            limit 
                10
        """
    if stat == 're':
        cmd = """

            select 
                sum(re) as total, school, last_name, first_name
            from 
                playerstats
            group by
                school, last_name, first_name
            order by 
                total desc
            limit 
                10
        """

    cur = conn.cursor()

    ## call execute and pass in as a tuple, arguments to the command string
    cur.execute(cmd)  # trailing comma to make it a tuple

    table = [("total", "school", "last_name", "first_name")]
    for row in cur:
        newrow = [unescape(str(i)) for i in row]
        table.append(newrow[0:4])
    print("\n")
    print(tabulate(table, tablefmt='fancy_grid', headers="firstrow"))


## gets kills over time regression for an inputted last name and schoool
## example player last name with school
## Ehnstrom,  Vassar
## Piper, St. Lawrence
## Werdine, Clarkson

def kills_time(conn):

    last_name = input("Enter a players last name: ")
    last_name = last_name.lower()

    school = input("Enter a school name for that player: ")
    school = school.lower()

    cmd = """
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
            lower(last_name) = cast(%s as varchar) and lower(school) = cast(%s as varchar)
        """

    cur = conn.cursor()

    ## call execute and pass in as a tuple, arguments to the command string
    cur.execute(cmd, (last_name,school))  # trailing comma to make it a tuple

    table = [("slope", "intercept","rsqrd" ,"count", "avgkills")]
    for row in cur:
        newrow = [unescape(str(i)) for i in row]
        table.append(newrow[0:5])
    print("\n")
    print(tabulate(table, tablefmt='fancy_grid', headers="firstrow"))

##output a JSON object -- given school get roster
## can be done for many different cols/tables
def json_dump(conn):
    school = input("Enter a School: ")
    school = school.lower()

    cmd = """
        SELECT *
        from 
            players
        where 
            lower(school) = %s
    """

    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute(cmd, (school,))

    print(dumps(cur.fetchall()))


##output a JSON object -- get team info given league
def json_dump2(conn):
    cmd = """
          SELECT *
          from 
              teams
          where 
              League = 'LibertyLeague'
      """

    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute(cmd)

    print(dumps(cur.fetchall()))


## if this file is being run as a program and *not* imported as a module
if __name__ == "__main__":

    conn = connect_ratings()

    opt_map = {'1': select_tbl,'2': lib_league_records, '3': attendance_reg, '4': set_stats_winner, '5':lib_stats, '6':player_stats,'7':regress_aces,'8':roster_stats, '9': player_stat10, '10':kills_time, '11': json_dump, '12': json_dump2 }
    while True:
        opt = menu()  ##opt either 1,2,q,Q
        # do something for quit
        opt_map[opt](conn)
    ## if opt == '1':
    ##lookup_by_title(conn)

