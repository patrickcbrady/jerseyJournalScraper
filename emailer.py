import csv
import os
import pickle
import re
import smtplib
from collections import defaultdict
from itertools import chain
from textwrap import wrap
from typing import Optional, List, Tuple

import arrow
from frozendict import frozendict

CATEGORIES = frozendict({'Ordinances': ['ordinance'], 'Variances': ['variance'], 'RFPs': ['request for pro'],
                         'Auctions': ['auction', 'sheriff\'s sale']})
LB = '\n'
AD_LINE_LEN = 120
CAT_DELIM = '-' * 80
AD_DELIM_BARE = '=' * AD_LINE_LEN
AD_DELIM = LB * 2 + AD_DELIM_BARE + LB * 2


def get_empty_body(week: str) -> str:
    return f'No Weehawken-related listings found for the week of {week}'


def get_subscriber_list() -> List[str]:
    with open('./subscribers') as f:
        reader = csv.reader(f)
        emails = list(chain.from_iterable([list(row) for row in reader]))
        return emails


def get_credentials() -> Tuple[str, str]:
    return open('./deviceu', 'r').read().replace(LB, ''), open('./devicepw', 'r').read().replace(LB, '')


def get_body_for_week(week: str, file: str) -> str:
    body = get_email_body(file)
    if not body:
        print(f'No listings for week of {week}')
        body = get_empty_body(week)
    return body


def get_email_text(sent_from: str, send_to: str, subject: str, body: str) -> str:
    return LB.join(["From: " + sent_from, "To: " + ", ".join(send_to), "Subject: " + subject, LB, body])


def send_email_for_file(file):
    week = os.path.basename(file)
    subject = f'Weehawken Public Notices for Week of {week}'
    body = get_body_for_week(week, file)
    send_email_to_subscribers(subject, body, f'Email sent successfully for {week}')


def send_email_to_subscribers(subject: str, body: str, success_msg: Optional[str] = None):
    gmail_user, gmail_pw = get_credentials()
    send_to = get_subscriber_list()
    email_text = get_email_text(gmail_user, send_to, subject, body)
    send_email(gmail_user, gmail_pw, send_to, email_text)
    if success_msg:
        print(success_msg)


def send_email(gmail_user, gmail_pw, send_to, email_text):
    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server.ehlo()
    server.login(gmail_user, gmail_pw)
    server.sendmail(gmail_user, send_to, email_text.encode('utf-8'))
    server.close()


def get_email_body(file: str) -> str:
    body = None
    date = os.path.basename(file)

    def is_recent(ad: str) -> bool:
        def last_date_to_arrow(last_date: str):
            for fmt in ('MM/DD/YY', 'M/DD/YY', 'MM/D/YY', 'M/D/YY', 'MM/DD/YYYY', 'M/DD/YYYY', 'MM/D/YYYY', 'M/D/YYYY'):
                try:
                    return arrow.get(last_date, fmt)
                except arrow.parser.ParserMatchError:
                    pass

        ad_date_str = find_last_date_in_ad(ad)
        if ad_date_str is None:
            return True
        ad_date = last_date_to_arrow(ad_date_str)
        last_week = arrow.get(date).shift(days=-7)
        res = ad_date > last_week
        # print(f'Is {ad_date.format("YYYY/MM/DD")} after '
        #      f'{last_week.format("YYYY/MM/DD")}? {"YES" if res else "NO"}')
        return res

    if os.path.getsize(file) > 0:
        with open(file, 'rb') as pickle_file:
            ad_list = pickle.load(pickle_file)
            ads = set(ad_list)
            print(f'{len(ads)} ads found.')
            ad_dict = get_ads_by_category(ads)
            body = get_ads_string(ad_dict)
    return body


def get_ads_by_category(ads: set) -> List[str]:
    result = defaultdict(list)
    for cat in CATEGORIES.keys():
        for match in CATEGORIES[cat]:
            for ad in ads:
                if match in ad.lower():
                    result[cat].append(ad)
            for ad in result[cat]:
                ads.discard(ad)
    result['Miscellaneous'] = list(ads)
    return result


def get_ads_string(ad_dict) -> str:
    result = ''
    for cat in ad_dict.keys():
        result += CAT_DELIM + LB + cat.upper() + LB + CAT_DELIM + LB + group_ads(ad_dict[cat]) + LB
    return result


def group_ads(ad_list) -> str:
    result = AD_DELIM_BARE + LB
    if ad_list:
        wrap_list = [LB.join(wrap(ad, AD_LINE_LEN)) for ad in ad_list]
        result += AD_DELIM.join(wrap_list).strip()
    else:
        result += 'None'
    result += AD_DELIM
    return result


def test_categories(file):
    with open(file, 'rb') as pickle_file:
        ad_list = pickle.load(pickle_file)
        result = get_ads_by_category(ad_list)
        print({k: len(v) for k, v in result.items()})
        print(get_ads_string(result))


def find_last_date_in_ad(ad: str) -> Optional[str]:
    match = None
    for match in re.finditer(r'\d{1,2}/\d{1,2}/\d{2,4}', ad):
        pass
    return None if not match else match.group(0)
