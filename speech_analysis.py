import pandas as pd
import re
from selenium import webdriver
from textblob import TextBlob
from langdetect import detect
from langdetect import detect_langs
from nltk.corpus import stopwords
import time
from nltk.tokenize import TweetTokenizer
def extract(length): #Length is the number of speeches to be extracted
    driver=webdriver.Chrome(executable_path=PATH)#Path of chromedriver.exe(For Chrome)
    url = "https://www.pmindia.gov.in/en/tag/pmspeech/"
    driver.get(url) #Opens the url in the driver window
    content_area = driver.find_elements_by_class_name('news-description')#Fetches a list of web content for each element with class name 'news-description'
    while len(content_area)<length: #While number of total speeches fetched is less than the input, scroll down the page
        SCROLL_PAUSE_TIME =0.5 
        last_height = driver.execute_script("return document.body.scrollHeight") # Gets scroll height
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);") # Scrolls down to bottom
        time.sleep(SCROLL_PAUSE_TIME) # Wait to load page
        new_height = driver.execute_script("return document.body.scrollHeight") # Calculates new scroll height and compares it with last scroll height
        last_height = new_height
        content_area = driver.find_elements_by_class_name('news-description')
    extract=[]
    for content in content_area: 
        text=content.find_element_by_tag_name('h3').text #Gets the headline of the speech
        href_tag=content.find_element_by_tag_name('h3>a')
        href=href_tag.get_attribute('href') #Gets the link of the speech
        date=content.find_element_by_tag_name('span').text #Gets the date on which the speech is made
        extract.append([date,text,href])
    df=pd.DataFrame()
    df['date']=[item[0] for item in extract]
    df['text']=[item[1] for item in extract]
    df['href']=[item[2] for item in extract]
    i=0
    df['news']=''
    while i<len(df): #Runs a loop to extract the speech text
        url=df.iloc[i,2]
        driver.get(url)
        try:
            news=driver.find_element_by_class_name('news-bg')
            df['news'][i]=news.text
        except:
            df['news'][i]='Link Corrupted' #If the speech can't be extracted
        i=i+1
    driver.quit() #Closing the driver
    df['lang']='' 
    for index,row in df.iterrows():
        df['lang'][index]=detect(row[3]) #To detect the language in which the speech is made
        if df['lang'][index]!='en': #If the speech is in 'Hindi'
            row[3]=str(TextBlob(row[3]).translate(to='en')) #translate it to 'English'
    df1=pd.DataFrame((df.iloc[0:length,:])['news'])
    tknzr = TweetTokenizer()
    df1['text']=df1['news'].apply(lambda x: " ".join(word.lower() for word in x.split())) 
    df1['text'] = df1['text'].apply(lambda x: re.sub(r'[^a-zA-Z0-9\s]', ' ', x)) #Removing all regex symbols
    stop=stopwords.words('english')
    df1['text'] = df1['text'].apply(lambda x: " ".join(x for x in x.split() if x not in stop)) #Removing all stopwords
    df1['text']=df1['text'].apply(lambda x: tknzr.tokenize(x)) #Tokenize all the words
    df1=list(df1['text'])
    word2count = {}
    total=0
    for data in df1: #Counting the occurence of each word
        words = data 
        for word in words:
            total=total+1
            if word not in word2count.keys(): 
                word2count[word] = 1
            else: 
                word2count[word] += 1
    freq_word={} #Getting the frequency of each word wrt to the total words uttered.
    for key,value in word2count.items():
        freq_word[key]=value/total
    k=''
    while k!='no':
        word=input("Enter a word : ").lower()
        try:
            print("The word", word,"occured a total of", word2count[word],"times in", len(df1),"speeches.\nThe frequency of word", word,"is",freq_word[word])
        except:
            print("This word was not said in any of the extracted speeches.")
        k=input("Press enter to continue or 'no' to end. ").lower()
extract(50)
