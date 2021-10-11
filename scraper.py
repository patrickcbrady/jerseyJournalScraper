import week
from lxml import html
import requests
import os
import pickle
from itertools import chain 

def getJerseyJournalListings():
    """
    As of 10/10/2021 the classifieds section has been revised to a new system that uses 
    images that may or may not have transcriptions inside of a show more link
    to-do: walk through results for weehawken keyword search, collect post dates and show more links.
    Visit each show more link and either collect the transcript or collect and OCR the image?
    """
    jjDomain = 'http://classifieds.nj.com'
    jjPath = '/marketplace/nj/search/query?categoryId=2&searchProfile=general&source=nj&page=1&size=100&view=list&showExtended=false&startRange=&keywords=weehawken&location=&postCode=&searchRadius=&searchUnit=MILES&customField1=&customField2=&customField3=&customField4=&customField5=&customField6=&customField7=&customField8=&customField9=&customField10=&ordering='
    # jjPath = '/?tp=ME_nj&cur_cat=6869&category=results&property=nj.com&temp_type=browse&ads_per_page=100'
    listings = getWeehawkenListingsForSite(jjDomain, jjPath)
    return listings

def getWeehawkenListingsForSite(jjDomain, jjPath):
    ad_lists = list()
    while not (not jjPath):
        jjUrl = jjDomain + jjPath
        tree = getPageTree(jjUrl)
        ad_lists.append(getListOfWeehawkenAdText(jjDomain, tree))
        jjPath = getNextPath(tree)
    result = list(chain.from_iterable(ad_lists))
    return result

def getListOfWeehawkenAdText(domain, tree):
    result = list()
    links = getWeehawkenHrefs(tree)
    for link in links:
        result.append(getFullAdTextFromInfoPage(domain + link))
    return result

def getWeehawkenHrefs(tree):
    hrefs = tree.xpath('//text()[contains(translate(., "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz"), "weehawken")]/ancestor::div[@class="result_box"]//a[@title="More Info"]/@href')
    return hrefs

def getFullAdTextFromInfoPage(infoPageUrl):
    tree = getPageTree(infoPageUrl)
    text = tree.xpath('//div[@class="adtext_pad"]/descendant::*/text()[normalize-space()]')
    return ' '.join(text);

def getPageTree(jjUrl):
    page = requests.get(jjUrl)
    return html.fromstring(page.content)

def getNextPath(tree):
    nextNodes = tree.xpath('//a[@title="Next"]/@href')
    if not nextNodes:
        return None
    else:
        return nextNodes[0]

def createFile():
    name = week.getCurrentWeek()
    try:
        file = open("./unsent/"+name, 'rb')
        print("file for this week exists. Exiting.")
        return
    except (IOError, FileNotFoundError):
        file = open("./unsent/"+name, 'wb')
        listings = getJerseyJournalListings()
        pickle.dump(listings, file)

createFile()
