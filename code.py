import pandas as pd
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

data = pd.read_excel('Input.xlsx')
data1=[]
#---------------------main program-----------------------------------------#
for i in range(len(data)):
    url40 = data['URL'][i]
    page40 = requests.get(url40)
    if page40.status_code == 200:
        soup40 = BeautifulSoup(page40.content, 'html.parser')
        content40 = soup40.findAll(attrs = {'class' : 'td-post-content'})
        content40 = content40[0].text.replace('\n',' ')
        if soup40.find(attrs = {'class' : 'wp-block-preformatted'}) is not None:
            f40 = soup40.find(attrs = {'class' : 'wp-block-preformatted'}).text
            content40 = content40.replace(f40,' ')

            file40 = open(str(data['URL_ID'][i])+'.txt','w',encoding='utf-8')
            file40.write(content40)
            file40.close()
            data1.insert(int(data['URL_ID'][i]),[data['URL_ID'][i], url40, content40])
            
        else:
            file40 = open(str(data['URL_ID'][i])+'.txt','w',encoding='utf-8')
            file40.write(content40)
            file40.close()
            data1.insert(int(data['URL_ID'][i]),[data['URL_ID'][i], url40, content40])
            
            
    else:
        print('URL' , data['URL_ID'][i],  'not valid')
#------------------------end--------------------------------------------#

#putting the data in a DataFrame  
df = pd.DataFrame(data1, columns=['URL_ID','URL','TEXT'])

#importing necessary libraries
import re
import string
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
#defining the stopwords
stop_words = set(stopwords.words('english'))
#to remove punctuation marks
p=str.maketrans('','',string.punctuation)   
#to remove more than one white spaces
df['TEXT'] = df['TEXT'].str.replace(r'\s+', ' ', regex=True)

#--------------TO CALCULATE THE POSITIVE SCORE---------------#
from nltk.sentiment.vader import SentimentIntensityAnalyzer
def ps(t):
    t = t.translate(p)
    t = t.lower()
    t = re.sub('\d+','',t)
    words_tokens=word_tokenize(t)   #splitting the text into words
    word_list = [w for w in words_tokens if w not in stop_words]
    t = ' '.join(word_list)
    score = SentimentIntensityAnalyzer().polarity_scores(t)
    return score['pos']
df['POSITIVE SCORE'] = df['TEXT'].apply(ps)

#--------------TO CALCULATE THE NEGATIVE SCORE--------------#
def ns(t):
    t = t.translate(p)
    t = t.lower()
    t = re.sub('\d+','',t)
    words_tokens=word_tokenize(t)   #splitting the text into words
    word_list = [w for w in words_tokens if w not in stop_words]
    t = ' '.join(word_list)
    score = SentimentIntensityAnalyzer().polarity_scores(t)
    return score['neg']
df['NEGATIVE SCORE'] = df['TEXT'].apply(ns)

#--------------TO CALCULATE THE POLARITY SCORE-------------------#
df['POLARITY SCORE'] = (df['POSITIVE SCORE']- df['NEGATIVE SCORE'])/((df['POSITIVE SCORE']+df['NEGATIVE SCORE'])+0.000001)

#--------------TO CALCULATE THE SUBJECTIVITY SCORE-----------------#
def sbj(t):
    t = t.translate(p)
    t = t.lower()
    t = re.sub('\d+','',t)
    words_tokens=word_tokenize(t)   #splitting the text into words
    word_list = [w for w in words_tokens if w not in stop_words]
    t = ' '.join(word_list)
    n = len(t)
    return n

df['SUBJECTIVITY SCORE'] = (df['POSITIVE SCORE']+df['NEGATIVE SCORE'])/((df['TEXT'].apply(sbj))+0.000001)

#--------TO CALCULATE AVERAGE SENTENCE LENGTH------------#
def avgno(text):
    s = re.split(r'[.!?]+', text)
    text = text.translate(p)
    text = re.sub('\d+','',text)
    w2 = nltk.tokenize.word_tokenize(text)
    avgNo = len(w2)/len(s)
    return avgNo

df['AVG SENTENCE LENGTH'] = df['TEXT'].apply(avgno)

#-------------TO CALCULATE PERCENTAGE OF COMPLEX WORDS---------------#
def syl_cnt(word):
  c = 0
  vowels = 'aeiou'
  l = re.findall(f'(?!e$)(?!es$)(?!ed$)[{vowels}]', word, re.I)
  return len(l)

def per(text):
    text = text.translate(p)
    text = re.sub('\d+','',text)
    text = text.lower()
    words = nltk.tokenize.word_tokenize(text)
    comp_cnt=[]
    for word in words:
        if word not in stop_words:
            n = syl_cnt(word)
            if n>2:
                list2 = []
                list2.append(word)
                list2.append(syl_cnt(word))
                comp_cnt.append(list2)
    return(len(comp_cnt)/len(words))

df['PERCENTAGE OF COMPLEX WORDS'] = df['TEXT'].apply(per)

#--------------TO CALCULATE FOG INDEX-------------#
df['FOG INDEX'] = 0.4*(df['AVG SENTENCE LENGTH'] + df['PERCENTAGE OF COMPLEX WORDS'])

#------------AVERAGE NUMBER OF WORDS PER SENTENCE------------#
df['AVG NUMBER OF WORDS PER SENTENCE'] = df['TEXT'].apply(avgno)

#-----------TO COUNT COMPLEX WORD COUNT--------------#
def comp(text):
    text = text.translate(p) 
    text = re.sub('\d+','',text)
    text = text.lower()
    words2 = word_tokenize(text)
    comp_cnt=[]
    for word in words2:
        if word not in stop_words:
            n = syl_cnt(word)
            if n>2:
                list2 = []
                list2.append(word)
                list2.append(syl_cnt(word))
                comp_cnt.append(list2)
    return len(comp_cnt)

df['COMPLEX WORD COUNT'] = df['TEXT'].apply(comp) 

#--------------TO COUNT WORDS----------------#
def cw(text):
    count=0
    text = text.translate(p)
    text = re.sub('\d+','',text)
    text = text.lower()
    words1 = word_tokenize(text)
    for word in words1 :
        if word not in stop_words:
            count+=1
    return count

df['WORD COUNT'] = df['TEXT'].apply(cw)

#---------------TO CALCULATE SYLLABLE PER WORD---------------#
def syl_cnt(word):
  c = 0
  vowels = 'aeiou'
  l = re.findall(f'(?!e$)(?!es$)(?!ed$)[{vowels}]', word, re.I)
  return len(l)

def sc(w):
    w = w.translate(p)
    w = re.sub('\d+','',w)
    filtered_words = []
    syllable_per_word = []
    words = word_tokenize(w)
    for word in words:
        if word not in stop_words:
            filtered_words.append(word)
            list1 = []
            list1.append(word)
            list1.append(syl_cnt(word))
            syllable_per_word.append(list1)
    return syllable_per_word

df['SYLLABLE PER WORD'] = df['TEXT'].apply(sc) 

#--------------TO CALCULATE PERSONAL PRONOUNS-----------------#
def pp(text):
    text = text.translate(p)   
    pro_count = re.compile(r'\b(I|we|ours|my|mine|(?-i:us))\b', re.I)
    pronouns = pro_count.findall(text)
    return len(pronouns)

df['PERSONAL PRONOUNS'] = df['TEXT'].apply(pp)

#----------------TO CALCULATE AVERAGE WORD LENGTH----------------#
def avg(text):
    text = text.translate(p)
    text = re.sub('\d+','',text)
    words = text.split()
    average = sum(len(word) for word in words) / len(words)
    return average

df['AVERAGE WORD LENGTH'] = df['TEXT'].apply(avg)
    
#-------------CONVERTING THE DATAFRAME TO EXCEL FILE------------#
df.to_excel('C:\\Users\\ragin\\OneDrive\\Desktop\\Intern\\Output1.xlsx',index=False)

