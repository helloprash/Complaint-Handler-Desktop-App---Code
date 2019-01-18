import os, sys, inspect, time  
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
import urllib3
from bs4 import BeautifulSoup as BS

current_folder = os.path.realpath(os.path.abspath(os.path.split(inspect.getfile(inspect.currentframe() ))[0]))

def checkSession(htmlSource):
    soup = BS(htmlSource, "lxml")
    try:
        tables = soup.find_all('table',{'id':'TBLoginForm'})
        data = ''
        td = [tr.find_all('td', {'class':'msgerror'}) for tr in tables[0].find_all('tr')]
        for eachtd in td:
            if eachtd:
                data = eachtd[0].text.strip()
        return False, data

    except:
        return True, 'None'

def preview(CFnum, main_url):
    print('Preview: ',preview)
    pjs_file = '\\\\'.join(os.path.join(current_folder,"chromedriver.exe").split('\\'))
    chrome_options = Options()
    #chrome_options.add_argument("--headless")
    #chrome_options.add_argument("--window-size=1920x1080")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("disable-extensions")
    try:
        browser = webdriver.Chrome(pjs_file, chrome_options=chrome_options)
        browser.implicitly_wait(3)
        browser.set_page_load_timeout(100)
        browser.get(main_url)

        browser.find_element_by_xpath("//input[contains(@id,'sb_form_q')]").send_keys(CFnum)#Bing
        browser.find_element_by_xpath("//input[contains(@id,'sb_form_go')]").click()
       
        print(browser.current_url)
        return True, 'None'

    except (urllib3.exceptions.TimeoutError, urllib3.exceptions.ReadTimeoutError):
        print('Read Timeout Error')
        return False, 'Read Timeout Error!'


def complaintProcess(CFnum, main_url):
    try:
        pjs_file = '\\\\'.join(os.path.join(current_folder,"phantomjs.exe").split('\\'))

        current_url = ''
        print('CFnum, main_url')
        print(CFnum, main_url)
        
        '''
        chrome_options = Options()
        #chrome_options.add_argument("--headless")
        #chrome_options.add_argument("--window-size=1920x1080")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("disable-extensions")
        browser = webdriver.Chrome(pjs_file, chrome_options=chrome_options)
        '''

        browser = webdriver.PhantomJS(executable_path = pjs_file)
        browser.set_page_load_timeout(100)
        browser.get(main_url)
        #browser.find_element_by_xpath("//input[contains(@title,'Search')]").send_keys(CFnum) #Google
        #browser.find_element_by_xpath("(//input[contains(@value,'Google Search')])[2]").click()
        
        browser.find_element_by_xpath("//input[contains(@id,'sb_form_q')]").send_keys(CFnum)#Bing
        browser.find_element_by_xpath("//input[contains(@id,'sb_form_go')]").click()
        current_url = browser.current_url
        browser.quit()
        print('---------------------------------------------')
        print(CFnum,current_url)
        
        return True,CFnum,current_url,True

    except: #ReadTimeoutError:
         return True, CFnum,'Error!', False

def Login(ID, password):
    print(ID, password)

    url = 'https://www.bing.com/'
    '''
    try :
        browser = webdriver.PhantomJS(executable_path = pjs_file)
        browser.set_page_load_timeout(100) 
        browser.get(url)
          

    except urllib3.exceptions.TimeoutError as e:
        print("Page load Timeout Occured. Quiting !!!")
        browser.quit()
        return (None, False)

    browser.find_element_by_xpath('//*[@id="CTRLemployeeid"]').send_keys(ID)
    browser.find_element_by_xpath('//*[@id="CTRLPasswordPrompt"]').send_keys(password)
    browser.find_element_by_xpath('//*[@id="TBLoginForm"]/tbody/tr[6]/td[2]/button').click()

    browser.save_screenshot('temp.png')

    print(browser.current_url)
    if browser.current_url == 'http://cwqa/CATSWebNET/main.aspx?WCI=Main&WCE=Login':
        return (None, False)
    else:
        return (browser.current_url, True)
   
    #random.seed(datetime.now()) 
    #str(random.random())
    '''
    return ('Successfully logged in',url, True)
        

def Logout(browser):
    browser.find_element_by_xpath('//*[@id="TBTopTable"]/tbody/tr[1]/td[3]/a[2]/font').click()
    browser.quit()




        
    
    
    

