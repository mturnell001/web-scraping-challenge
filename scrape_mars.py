from splinter import Browser
from bs4 import BeautifulSoup as bs
import time
import re
import pandas as pd

def init_browser():
    '''Initialize a splinter Chrome browser'''
    return Browser("chrome", headless=True)

def scrape_soup(url):
    '''Use bs4 and splinter to visit the given url and return the soup
    html object'''
    
    with init_browser() as browser:

        browser.visit(url)

        time.sleep(2)

        # Scrape page into Soup
        html = browser.html
        soup = bs(html, "html.parser")
    
    return(soup)

def nasa_article_parser():
    '''Parse the mars NASA news site and return the article titles
    and the paragraph teasers'''
    
    url = "https://mars.nasa.gov/news/"

    #collect all the article titles
    news_titles = [div.get_text() for div in scrape_soup(url).find_all("div", class_="content_title")]

    #collect all the news article 'teaser' paragraphs
    p_teasers = [div.get_text() for div in scrape_soup(url).find_all("div", class_="article_teaser_body")]
    return(news_titles, p_teasers)

def jpl_img_scraper():
    '''Scrape the jpl site for the full-size of the featured image
    and return its url'''
    
    url = "https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars"
    #find the 'full image' button, click it, and soupify the resulting page
    with init_browser() as browser:
        browser.visit(url)
        time.sleep(2)
        browser.find_by_id('full_image')[0].click()
        time.sleep(2)
        html = browser.html
        soup = bs(html, "html.parser")

    #find the big image and construct the full URL from the relative url
    feat_img = soup.find_all("img", class_="fancybox-image")[0]["src"]
    feat_img_url = "https://www.jpl.nasa.gov" + feat_img
    
    return(feat_img_url)

def mars_weather_tweet():
    '''Scrapes the Mars Weather twitter for the latest tweet and returns
    its text'''
    
    #soupify the twitter page
    url = "https://twitter.com/marswxreport?lang=en"
    soup = scrape_soup(url)

    #find all the tweet "boxes"
    tweets = soup.find_all("li", attrs={"class":"js-stream-item"})

    #get the text from the most recent tweet
    #will break if they ever pin a tweet
    latest_tweet = [tweet.find("p", class_="tweet-text").get_text() for tweet in tweets][0]
    
    #if there's a picture URL in the tweet, drop it
    if "pic.twitter.com" in latest_tweet:
        latest_tweet = latest_tweet.split("pic.twitter.com")[0]
        
    return(latest_tweet)
      
def space_facts_scrape():
    '''Scrapes the table of facts into a pandas df, then
    returns a string of HTML containing the dataframe'''

    #soupify the page
    url = "https://space-facts.com/mars/"
    soup = scrape_soup(url)
    
    #find the table
    planet_table = soup.find("table", id="tablepress-p-mars-no-2")
    
    #pandafy the table
    planet_df = pd.read_html(str(planet_table))[0]
    
    #label the columns
    planet_df.columns=["Category", "Value"]
    
    #htmlify the database
    df_html = planet_df.to_html(index=False)

    return(df_html)

def usgs_hemisphere_scraper():
    '''Navigates the usgs website and scrapes the full URLs
    of all 4 enhanced-resolution hemisphere pictures'''
    
    url = "https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars"
    with init_browser() as browser:

            #start with an empty list of dictionaries
            image_dict = []
            
            #keep going until we have all 4 images
            while len(image_dict) < 4:
                
                #visit the page and find all 4 "enhanced" links
                browser.visit(url)
                time.sleep(2)
                image_links = browser.links.find_by_partial_text('Enhanced')

                #click the next link
                image_links[len(image_dict)].click()
                time.sleep(2)
                
                #click the "open" button to access the full-res image
                browser.links.find_by_href("#open")[0].click()
                html = browser.html
                
                #soupify the page
                soup = bs(html, "html.parser")
                
                #find the big image and construct the full URL from the relative url
                large_img = soup.find_all("img", class_="wide-image")[0]["src"]
                img_url = "https://astrogeology.usgs.gov" + large_img
                
                #do some parsing on the title, then pass the title and url
                #to our dictionary
                title = browser.title
                title = title.split(' |')[0]
                image_dict.append({"title" : title, "url" : img_url})

    return(image_dict)            
            
def scrape():
    '''Runs all of the scraping functions, compiles the result
    into a dictionary, then returns.'''

    nasa_article_info = nasa_article_parser()
    recent_title = nasa_article_info[0][0]
    recent_article = nasa_article_info[1][0]

    feat_img_url = jpl_img_scraper()

    latest_tweet = mars_weather_tweet()

    facts_table_html = space_facts_scrape()

    hemisphere_image_dict = usgs_hemisphere_scraper()

    nasa_dict = {"recent_title" : recent_title,
                 "recent_article" : recent_article,
                 "feat_img_url" : feat_img_url,
                 "latest_tweet" : latest_tweet,
                 "facts_table_html" : facts_table_html,
                 "hemisphere_image_dict" : hemisphere_image_dict}

    return(nasa_dict)