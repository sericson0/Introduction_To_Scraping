#Requires selenium and pandas
import time
import pandas as pd
from selenium import webdriver as wd
from selenium.webdriver.support.ui import Select
import selenium
import numpy as np
import os
#_______________________________________________________________________________________________________________________________________
#_______________________________________________________________________________________________________________________________________
#_______________________________________________________________________________________________________________________________________
#Inputs
csv_save_folder = "../Glassdoor Data"
os.chdir(os.path.dirname(os.path.abspath(__file__)))
if not os.path.exists(csv_save_folder): os.mkdir(csv_save_folder)

company_name_list = ["Wells Fargo", "Apple", "Ford Motor Company"]
#Number at the end of the reviews page. May be a way to automate this but will leave that to your own time
company_number_list = ["E8876", "E1138", "E263"]
#Limit is number of reviews to load (code is currently not robust to end point so limit needs to be smaller than the total number of reviews)
LIMIT = 30
#Your glassdoor username and password
#headless means the web browser wont open up
HEADLESS = True
HEADLESS = False
#SORT_OPTION = NA will default to Popular. Otherwise can input to sort by:
#		-Popular
#		-Hishest Rating
#		-Lowest Rating
#		-Most Recent
#		-Oldest First
# SORT_OPTION = "NA" 
SORT_OPTION = "Most Recent"
return_cols = ["full_text", "date", "review_title"]
#_______________________________________________________________________________________________________________________________________
#_______________________________________________________________________________________________________________________________________
#_______________________________________________________________________________________________________________________________________
def get_username_and_password(text_file = "./Username and Password.txt"):
    with open(text_file, "r") as f:
        username = f.readline().split(",")[1].strip()
        password = f.readline().split(",")[1].strip()
    return {"username":username, "password":password}

def scrape(field, review, author):
    def scrape_full_text(review):
        # print(review.text)
        return review.text

    def scrape_date(review):
        return review.find_element_by_tag_name(
            'time').get_attribute('datetime')

    def scrape_rev_title(review):
        return review.find_element_by_class_name('summary').text.strip('"')

  
    funcs = [
        scrape_full_text,
        scrape_date,
        scrape_rev_title,
    ]

    fdict = dict((s, f) for (s, f) in zip(return_cols, funcs))

    return fdict[field](review)


def extract_from_page():
    def extract_review(review):
        author = review.find_element_by_class_name('authorInfo')
        res = {}
        for field in return_cols:
            res[field] = scrape(field, review, author)

        assert set(res.keys()) == set(return_cols)
        return res

    res = pd.DataFrame([], columns=return_cols)

    reviews = browser.find_elements_by_class_name('empReview')
    for review in reviews:
        data = extract_review(review)
        res.loc[idx[0]] = data
        idx[0] = idx[0] + 1
    return res



def go_to_next_page(url):
    page[0] = page[0] + 1
    browser.get(url+"_P"+str(page[0])+".htm")
    time.sleep(1)




def sign_in(credentials):
    url = 'https://www.glassdoor.com/profile/login_input.htm'
    browser.get(url)

    username_field = browser.find_element_by_name('username')
    password_field = browser.find_element_by_name('password')
    submit_btn = browser.find_element_by_xpath('//button[@type="submit"]')

    username_field.send_keys(credentials["username"])
    password_field.send_keys(credentials["password"])
    submit_btn.click()
    time.sleep(1)


def get_browser():
    chrome_options = wd.ChromeOptions()
    if HEADLESS == True:
        chrome_options.add_argument('--headless')
    chrome_options.add_argument('log-level=3')
    browser = wd.Chrome(options=chrome_options)
    return browser


def sort_reviews(option):
    selection_options = Select(browser.find_element_by_id("FilterSorts"))
    selection_options.select_by_visible_text(option)
    time.sleep(1)

def get_company_reviews(company_name, company_number, csv_file_name):
    page[0] = 1
    idx[0] = 0
    print(f'Scraping up to {LIMIT} reviews for {company_name}.')

    res = pd.DataFrame([], columns=return_cols)
    url = "https://www.glassdoor.com/Reviews/"+company_name.replace(" ","-")+"-Reviews-"+company_number
    browser.get(url+".htm")
    time.sleep(1)
    #
    if SORT_OPTION != "NA":
        sort_reviews(SORT_OPTION)

    reviews_df = extract_from_page()
    res = res.append(reviews_df)

    while len(res) < LIMIT:
        go_to_next_page(url)
        reviews_df = extract_from_page()
        res = res.append(reviews_df)

    res.to_csv(csv_file_name, index=False, encoding='utf-8')


def get_all_company_reviews(company_name_list, company_number_list, csv_save_folder, credientials):
    csv_file_names = [csv_save_folder + "/" + company_name + ".csv" for company_name in company_name_list] 

    sign_in(credientials)
    for i in range(len(company_name_list)):
    	get_company_reviews(company_name_list[i], company_number_list[i], csv_file_names[i])
    print('finished running code!!!')
    browser.quit()

credientials = get_username_and_password()
page = [1]
idx = [0]
browser = get_browser()
get_all_company_reviews(company_name_list, company_number_list, csv_save_folder, credientials)
