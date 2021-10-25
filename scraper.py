import os
import pickle
from typing import List

import arrow
import requests
from lxml import html

import week

HEADERS = {'authority': 'classifieds.nj.com',
           'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36',
           'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'}


def get_jersey_journal_listings() -> List[str]:
    """
    return the text of each Weehawken public notice listing for the current week
    """
    jj_domain = 'https://classifieds.nj.com'
    jj_path = '/marketplace/nj/search/query?categoryId=2&searchProfile=general&source=nj&page=1&size=100&view=list&showExtended=false&startRange=&keywords=weehawken&customField1=The+Jersey+Journal'
    listings = get_weehawken_listings_for_site(jj_domain, jj_path)
    return listings


def get_weehawken_listings_for_site(jj_domain, jj_path) -> List[str]:
    result = []
    jj_url = f'{jj_domain}{jj_path}'
    tree = get_page_tree(jj_url)
    ad_links = tree.xpath('//div[@class="thumbnail-container"]//a//@href')
    ad_dates = tree.xpath('//span[@class="time-stamp"]//time//@datetime')
    current_week = arrow.get(week.get_current_week())
    for i, link in enumerate(ad_links):
        # links are retrieved in order so we can break early once we're past our date range
        ad_date = arrow.get(ad_dates[i])
        age_days = (current_week - ad_date).days
        # site format changed on 10/10 so ensure that first run after fix will backfill
        if age_days >= 8 and current_week > arrow.get('2021-10-24'):
            break
        elif ad_date < arrow.get('2021-10-03'):
            break
        result.append(get_full_ad_text_info_from_page(link))
    return result


def get_full_ad_text_info_from_page(info_page_url) -> str:
    """return text of public notice listing from full ad listing URL"""
    tree = get_page_tree(info_page_url)
    text = tree.xpath('//*[contains(@class, "sr_ad_content")]/div[@class="panel-body"]//text()[normalize-space()]')
    return '\n'.join(text)


def get_page_tree(jj_url):
    """return tree for given NJ.com classifieds URL"""
    page = requests.get(jj_url, headers=HEADERS)
    return html.fromstring(page.content)


def create_file():
    name = week.get_current_week()
    f_path = f'./unsent/{name}'
    try:
        with open(f_path, 'rb') as file:
            print("file for this week exists. Exiting.")
            return
    except (IOError, FileNotFoundError):
        try:
            with open(f_path, 'wb') as file:
                listings = get_jersey_journal_listings()
                pickle.dump(listings, file)
        except KeyboardInterrupt:
            os.remove(f_path)


def __main():
    create_file()


if __name__ == '__main__':
    __main()
