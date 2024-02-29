# SYEvolleyball

## Project Description
   This project scraped and analyzed NCAA Division 3 Liberty League Volleyball Data for 2013-2022 seasons. 
   
## Data Files Key

- boxscoresFINAL.csv  = data files for boxscores data
- per_set_statsNEW.csv = data file for per set stats
- play_by_playFINAL3.csv = data file for play by play data
- individualsNEW.csv = data for individual player stats


## Coding Files

1. main_urls.Rmd
      - file contains functions:
          - get_first_google_link()
          - get_complete_match_urls()

2. complete_url_list_ALL.txt = file outputted in main_urls.Rmd and then used in the scraping functions within other RMDs


3. cleaned_boxscores.Rmd
      - file contains the functions:
        - scrape_url()
        - clean_boxscores()
        - save_boxscores()
                                    
4. cleaned_individuals.Rmd
      - file contains the functions:
        - scrape_url()
        - clean_individuals()
        - save_individuals() 
5. cleaned_per_set_stats.Rmd
      - file contains the functions:
        - scrape_url()
        - clean_persetstats()
        - save_persetstats()                   
                  
6. cleaned_play_by_play.Rmd
      - file contains the functions:
        - scrape_url()
        - clean_playbyplay()
        - save_playbyplay()
7. analysis.Rmd
      - file contains all analysis coding for graphs/regressions
8. cs345proj.Rmd
      - contains R code for the SQL visual representations                                  
9. final_python.py 
     - contains interface for users and theh queries to be ran within that
    
10. finalproject_cjrich19.sql
    - contains all SQL queries 
