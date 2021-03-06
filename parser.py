# -*- coding: utf-8 -*-
import urllib2
from bs4 import BeautifulSoup
import json
from time import sleep
import httplib
from codecs import getwriter
from sys import stdout

def patch_http_response_read(func):
    def inner(*args):
        try:
            return func(*args)
        except httplib.IncompleteRead, e:
            return e.partial

    return inner

httplib.HTTPResponse.read = patch_http_response_read(httplib.HTTPResponse.read)

BASE_URL = 'http://www.pechenuka.ru/'
receipt = []
def get_html(url):
    try:
        response = urllib2.urlopen(url)
    except urllib2.HTTPError as err:
        if err.code == 404:
            return "";
        else:
            sleep(15)
            return get_html(url)
    encoding = response.headers['content-type'].split('charset=')[-1]
    #responce_html = unicode(response.read(), encoding)
    responce_html = response.read().decode(encoding,'ignore')
    return responce_html.encode('utf-8')


def parse_receipt_imgs(html):
    soup = BeautifulSoup(html, "lxml")
    imgs = soup.find_all('img', class_='img-frame')
    if imgs is None:
        return [];
    images = []
    for img in imgs:
         images.append(img['src'])
    return images;

def parse_ingridients(html):
    soup = BeautifulSoup(html, "lxml")
    ingridients = soup.find('div', itemprop='ingredients')
    if ingridients is None:
        return [];
    ingridients = ingridients.text
    ingridientsResult = []
    ingrids = ingridients.split(', ');
    for ingrid in ingrids:
        ingridientsResult.append({
            'full': ingrid,
            })
    return ingridientsResult;

def parse_receipt_description(html):
    soup = BeautifulSoup(html, "lxml")
    descs_div = soup.find('div', class_='span8 detail')
    if descs_div is None:
        return [];
    descs = descs_div.find_all('p')
    description = ''
    for desc in descs:
         description = description + desc.text
    return description;

def parse_step_by_step_receipt(html):
    soup = BeautifulSoup(html, "lxml")
    div = soup.find('div', itemprop='recipeInstructions')
    if div is None:
        return [];
    steps = div.find_all('p')
    receipt_steps = []
    for step in steps:
        receipt_steps.append({
            'images': 'imgs',
            'description': step.text
            })
    return receipt_steps;
def get_page_count(html):
    soup = BeautifulSoup(html,"lxml")
    paggination = soup.find('div', class_='pagination pagination-centered pagination-large')
    if paggination is None:
        return 0;
    print(int(paggination.find_all('a')[-2].text))
    return int(paggination.find_all('a')[-2].text)

def parse_cat(html):
    soup = BeautifulSoup(html, "lxml")
    cat_page = soup.find('article')
    rows = cat_page.find_all('h2')
    for row in rows:
        col = row.find('a')
        receipt = []
        receipt_html = get_html(BASE_URL + col['href']);
        #receipt_html = get_html('http://www.pechenuka.ru/news/category/sup-pyure/');
        total_pages = get_page_count(receipt_html)
        if total_pages == 0:
            receipt.append({
                'url': col['href'],
                'name': col.text,
                'images': parse_receipt_imgs(receipt_html),
                "tags": [],
                "cuisine_by_nationality": [""],
                "type": [],
                "context": [],
                "skill" : "",
                "description": parse_receipt_description(receipt_html),
                "date": "",
                "cooking_time": "",
                "preparation_time": "",
                "number_of_servings": "",
                "ingredients":parse_ingridients(receipt_html),
                "step_by_step_recipe": parse_step_by_step_receipt(receipt_html),
            })
        else:
            receipt.append({
                'url': col['href'],
                'name': col.text,
                'images': parse_receipt_imgs(receipt_html),
                "tags": [],
                "cuisine_by_nationality": [""],
                "type": [],
                "context": [],
                "skill" : "",
                "description": parse_receipt_description(receipt_html),
                "date": "",
                "cooking_time": "",
                "preparation_time": "",
                "number_of_servings": "",
                "ingredients":parse_ingridients(receipt_html),
                "step_by_step_recipe": parse_step_by_step_receipt(receipt_html),
            })
            for page in range(2, total_pages + 1):
                receipt_html = get_html(BASE_URL + col['href'] + "page%d.html" % page)
                receipt.append({
                'url': col['href'],
                'name': col.text,
                'images': parse_receipt_imgs(receipt_html),
                "tags": [],
                "cuisine_by_nationality": [""],
                "type": [],
                "context": [],
                "skill" : "",
                "description": parse_receipt_description(receipt_html),
                "date": "",
                "cooking_time": "",
                "preparation_time": "",
                "number_of_servings": "",
                "ingredients":parse_ingridients(receipt_html),
                "step_by_step_recipe": parse_step_by_step_receipt(receipt_html),
                })
        sout = getwriter("utf8")(stdout)
        #print json.dumps(receipt, ensure_ascii=False)
        sout.write(json.dumps(receipt, ensure_ascii=False) + '\n')
        #stro = json.dumps(receipt,ensure_ascii=False)
        #stro = unicode(stro, "utf-8")
        #stro.encode('utf-8')
        #print stro
        #print stro
    
    
def parse_main(html):
    soup = BeautifulSoup(html, "lxml")
    cat_page = soup.find('dl', class_='catalogue isearch_scroll')
    rows = cat_page.find_all('dd')[1:]
    projects = []
    for row in rows:
        cols = row.find_all('a')[1:]
        for col in cols:
            parse_cat(get_html(BASE_URL + col['href']))

    
def main():
    parse_main(get_html(BASE_URL))

if __name__ == '__main__':
    main()
