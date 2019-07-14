import pickle
import smtplib
import os
import csv
from textwrap import wrap
from itertools import chain
from frozendict import frozendict

CATEGORIES = frozendict({'Ordinances': ['ordinance'], 'Variances':['variance'], 'RFPs':['request for pro'], 'Auctions':['auction', 'sheriff\'s sale']})
LB = '\n'
AD_LINE_LEN = 120
CAT_DELIM = '-'*80
AD_DELIM_BARE = '='*AD_LINE_LEN
AD_DELIM = LB*2 + AD_DELIM_BARE + LB*2

def get_subscriber_list():
	with open('./subscribers') as f:
		reader = csv.reader(f)
		emails = list(chain.from_iterable([list(row) for row in reader]))
		return emails

def send_email_for_week(week):
	send_email_for_file('./'+week)

def send_email_for_file(file):
    week = os.path.basename(file)
    gmail_user = open('./deviceu','r').read().replace(LB,'')
    gmail_pw = open('./devicepw','r').read().replace(LB,'')

    sent_from = gmail_user
    to = get_subscriber_list()
    subject = "Weehawken Public Notices for Week of %s" % (week)
    body = get_email_body(file) 
    email_text = LB.join(["From: "+sent_from, "To: " + ", ".join(to), "Subject: " + subject, LB, body])

    try:
        send_email(gmail_user, gmail_pw, to, email_text)
        print('Email sent Successfully for', week)
    except Exception as e:
        print('Something went wrong:', e)

def send_email(gmail_user, gmail_pw, to, email_text):
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(gmail_user, gmail_pw)
        server.sendmail(gmail_user, to, email_text.encode('utf-8'))
        server.close()

def get_email_body(file):
    body = None
    with open(file, 'rb') as pickle_file:
        ad_list = pickle.load(pickle_file)
        ad_dict = get_ads_by_category(ad_list)
        body = get_ads_string(ad_dict)
    return body

def get_ads_by_category(listings):
    result = {k: [] for k in CATEGORIES.keys()}
    ads = set(listings)
    for cat in CATEGORIES.keys():
        for match in CATEGORIES[cat]:
            for ad in ads:
                if match in ad.lower():
                    result[cat].append(ad)
            for ad in result[cat]:
                ads.discard(ad)
    result['Miscellaneous'] = list(ads)
    return result

def get_ads_string(ad_dict):
    result = ''
    for cat in ad_dict.keys():
        result += CAT_DELIM + LB + cat.upper() + LB + CAT_DELIM + LB + group_ads(ad_dict[cat]) + LB
    return result 

def group_ads(ad_list):
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

