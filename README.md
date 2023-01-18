# jerseyJournalScraper
A weekly script to scrape Weehawken-related clippings (legislation, etc.) from the paper of record in Hudson County

This app requires three plaintext files in the root directory to be filled out to be fully functional.

* deviceu
    * the username of a gmail account to be used to send emails
* devicepw
    * the password of a gmail account to be used to send emails (recommend using an app password, i.e. https://support.google.com/accounts/answer/185833?hl=en)
* subscribers
    * a comma-separated list of email addresses to send the ad summaries to
    
# How to Run
Once the three files are in place, run `python3 scraper.py` in the root directory to generate the scraped ads. Then, run `python3 send_unsent.py` to send a summary email for each unsent file. 
If anything goes wrong in send_unsent, the file will remain in the unsent directory. Requires Python 3.7 or later.
