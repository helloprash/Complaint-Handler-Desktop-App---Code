from pathlib import Path
import os,sys, inspect
from bs4 import BeautifulSoup as BS
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
import urllib3
from subprocess import Popen
import time
import steps


current_folder = os.getcwd()

def checkCM(htmlSource):
    soup = BS(htmlSource, "lxml")
    bold = soup.find_all('b')
    for eachText in bold:
        if eachText.text.strip() == 'Complaint Manager Home Page':
            return True
    return False

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


def actionSubmit(browser,ID):
    browser.find_element_by_id('CTRLRECORDTYPE2').click() #Action Radio
    browser.find_element_by_xpath('//*[@id="CTRLRECORDIDTO"]').send_keys(ID) #CWID 
    browser.find_element_by_xpath('//*[@id="CTRLSubmitCommonPageTop"]').click() #Submit
    return browser
    
def getCFDetails(htmlSource):
    try:
        soup = BS(htmlSource, "lxml")
        #soup = BS(open(file_path), "lxml")
        center = soup.find_all('center')
        tables = soup.find_all('table',{'id':'TBCALogForm'})

        #Username
        td = [tr.find_all('td', {'id':'TDAssignedTo'}) for tr in tables[0].find_all('tr')]
        for eachtd in td:
            if eachtd:
                data = [each.find('br').next_sibling for each in eachtd]
        username = data[0].text.strip()

        #Medical event
        td = [tr.find_all('td', {'id':'TDStandardText069'}) for tr in tables[0].find_all('tr')]
        for eachtd in td:
            if eachtd:
                data = [each.find('font') for each in eachtd]
        medical_event = data[0].text.strip()

        #pRE
        pREflag = False
        p_tag = soup.find(text='pREs').parent
        font_tag = p_tag.parent
        center_tag = font_tag.parent
        next_center_tag = center_tag.findNext('center').findNext('center')
        pREtables = next_center_tag.find('table',{'id':'TBGenericRecs0'})
        pREtr = pREtables.find_all('tr')

        for i in range(1, len(pREtr)):
            pREtd = [eachtd for eachtd in pREtr[i].find_all('td')]
            data = [item.text.strip() for item in pREtd]
            for j in range(3,13):
                if data[j] == 'Yes':
                    pREflag = True
        
        print(pREflag)

    

        #RDPC
        td = [tr.find_all('td', {'id':'TDStandardMemo013'}) for tr in tables[0].find_all('tr')]
        for eachtd in td:
            if eachtd:
                data = [each.find('font') for each in eachtd]
        RDPC = data[0].text.strip()
        
        #Current step
        td = [tr.find_all('td', {'id':'TDStandardText003'}) for tr in tables[0].find_all('tr')]
        for eachtd in td:
            if eachtd:
                data = [each.find('font') for each in eachtd]
        step = data[0].text.strip()

        #Product
        p_tag = soup.find(text='Products').parent
        font_tag = p_tag.parent
        center_tag = font_tag.parent
        next_center_tag = center_tag.findNext('center').findNext('center')
        tables = next_center_tag.find_all('table',{'id':'TBGenericRecs0'})
        td = [tr.find_all('td', {'id':'TDRowItem16'}) for tr in tables[0].find_all('tr')]
        td1 = [tr.find_all('td', {'id':'TDRowItem14'}) for tr in tables[0].find_all('tr')]
        td2 = [tr.find_all('td', {'id':'TDRowItem19'}) for tr in tables[0].find_all('tr')]
        for eachtd, eachtd1, eachtd2 in zip(td,td1,td2):
            if (eachtd, eachtd1, eachtd2):
                data = [each.find('font') for each in eachtd]
                data1 = [each.find('font') for each in eachtd1]
                data2 = [each.find('font') for each in eachtd2]
        productFormula = data[0].text.strip()
        productType = data1[0].text.strip()
        serialNum = data2[0].text.strip()

        #Investigation report
        try:
            ir_tag = soup.find(text='Investigation Requests').parent
            font_tag = ir_tag.parent
            center_tag = font_tag.parent
            next_center_tag = center_tag.findNext('center').findNext('center')
            tables = next_center_tag.find_all('table',{'id':'TBGenericRecs0'})
            td = [tr.find_all('td', {'id':'TDRowItem11'}) for tr in tables[0].find_all('tr')]
            td1 = [tr.find_all('td', {'id':'TDRowItem13'}) for tr in tables[0].find_all('tr')]
            for eachtd, eachtd1 in zip(td,td1):
                if (eachtd,eachtd1):
                    data = [each.find('font') for each in eachtd]
                    data1 = [each.find('font') for each in eachtd1]
            IRnum = data[0].text.strip()
            IRstep = data1[0].text.strip()
            IR = True
        except AttributeError:
            IR = False
            IRstep = 'XX'
            IRnum = 'XXXX'
        
        return(True,username,RDPC,medical_event,pREflag,step,productType,productFormula,serialNum,IR,IRstep,IRnum)
    except Exception as err:
        print(err)
        return(False,'username','RDPC','medical_event','pREflag','step','productType','productFormula','serialNum','IR','IRstep','IRnum')


def Login(ID, password):
    pjs_file = '\\\\'.join(os.path.join(current_folder,"phantomjs.exe").split('\\'))
    print(pjs_file)

    fileFlag = True
    my_file = Path(pjs_file)
    if not my_file.is_file():
        fileFlag = False
        print('fileError')
        return ('phantomjs.exe file not found',None, False,fileFlag)


    print(ID, password)
    url = 'http://cwqa/CATSWebNET/'
    #url = 'http://cwqa/CATSWebNET/main.aspx?WCI=Main&WCE=ViewDashboard&WCU=s%3dSA8IA9EM9TG18C4I98HEXMXU46CTV2XO%7c*~r%3dComplaint%20Owner%20Home%20Page%7c*~q%3d1'
    
    while True:
        try :
            browser = webdriver.PhantomJS(executable_path = pjs_file, desired_capabilities={'phantomjs.page.settings.resourceTimeout': '5000'})
            browser.implicitly_wait(3)
            browser.set_page_load_timeout(100) 
            browser.get(url)

            browser.find_element_by_xpath('//*[@id="CTRLemployeeid"]').send_keys(ID)
            browser.find_element_by_xpath('//*[@id="CTRLPasswordPrompt"]').send_keys(password)
            browser.find_element_by_xpath('//*[@id="TBLoginForm"]/tbody/tr[6]/td[2]/button').click()

            sessionFlag, returnMsg = checkSession(browser.page_source)
            if not sessionFlag:
                current_url = browser.current_url
                browser.quit()
                return (returnMsg, current_url, sessionFlag, fileFlag)

            return ('Please enter your login information:',browser.current_url, True, fileFlag)

              
        except (urllib3.exceptions.TimeoutError, urllib3.exceptions.ReadTimeoutError): 
            browser.quit()
            print("Page load Timeout Occured. Quiting !!!")
            continue
            #return ('Page load Timeout Occured. Please try again',None, False)

        except Exception as e:
            print(e)
            continue
            #return (e,None, False)
        '''
        finally:
            #Popen(batch_file)
            print('10 sleep')
            time.sleep(10)
        '''

    
    #return (url, True)

def preview(CFnum, main_url):
    print('Preview: ',preview)
    pjs_file = '\\\\'.join(os.path.join(current_folder,"chromedriver.exe").split('\\'))

    fileFlag = True
    my_file = Path(pjs_file)
    if not my_file.is_file():
        fileFlag = False
        print('fileError')
        return False, False, 'chromedriver.exe file not found', fileFlag

    chrome_options = Options()
    #chrome_options.add_argument("--headless")
    #chrome_options.add_argument("--window-size=1920x1080")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("disable-extensions")
    while True:
        try:
            browser = webdriver.Chrome(pjs_file, chrome_options=chrome_options)
            browser.implicitly_wait(3)
            browser.set_page_load_timeout(100)
            browser.get(main_url)

            sessionFlag, returnMsg = checkSession(browser.page_source)
            if not sessionFlag:
                if returnMsg == 'Your CATSWeb V7 session does not exist.  Please enter your login information:':
                    return sessionFlag, False, 'Your CATSWeb V7 session expired!', fileFlag
           
            print(browser.current_url)

            CM = checkCM(browser.page_source)
            if CM:
                browser.find_element_by_xpath('//*[@id="TDDisplayPart004"]/font/a/font').click() #Load Complaint Owner Home page

            browser = actionSubmit(browser,CFnum)
            return sessionFlag,True, 'None', fileFlag

        except (urllib3.exceptions.TimeoutError, urllib3.exceptions.ReadTimeoutError):
            print('Read Timeout Error')
            continue
            #return sessionFlag, False, 'Read Timeout Error!'

        except:
            continue


def complaintProcess(CFnum, url):
    print('inside complaintProcess', url)
    pjs_file = '\\\\'.join(os.path.join(current_folder,"phantomjs.exe").split('\\'))

    fileFlag = True
    my_file = Path(pjs_file)
    if not my_file.is_file():
        fileFlag = False
        print('fileError')
        return False, CFnum, 'phantomjs.exe file not found', False, fileFlag
    
    print(pjs_file)
    '''
    chrome_options = Options()
    #chrome_options.add_argument("--headless")
    #chrome_options.add_argument("--window-size=1920x1080")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("disable-extensions")
    '''
    
    while True:
        try:
            #browser = webdriver.Chrome(pjs_file, chrome_options=chrome_options)
            
            browser = webdriver.PhantomJS(executable_path = pjs_file, desired_capabilities={'phantomjs.page.settings.resourceTimeout': '5000'})
            browser.implicitly_wait(3)
            browser.set_page_load_timeout(100)

            browser.get(url)

            sessionFlag, returnMsg = checkSession(browser.page_source)
            if not sessionFlag:
                if returnMsg == 'Your CATSWeb V7 session does not exist.  Please enter your login information:':
                    return False, CFnum, 'session expired!', False, fileFlag
           
            print(browser.current_url)

            CM = checkCM(browser.page_source)
            if CM:
                browser.find_element_by_xpath('//*[@id="TDDisplayPart004"]/font/a/font').click()

            browser = actionSubmit(browser,CFnum)

            (flag, username,RDPC,medical_event,pREflag,current_step,productType,productFormula,serialNum,IR,IRstep,IRnum) = getCFDetails(browser.page_source)
            print(flag, username,RDPC,medical_event,pREflag,current_step,productType,productFormula,serialNum,IR,IRstep,IRnum)
            break

        except (urllib3.exceptions.TimeoutError, urllib3.exceptions.ReadTimeoutError):
            print('Read Timeout Error')
            browser.quit()
            continue
            #return (True, CFnum, 'Read Timeout Error', False)

        except NoSuchElementException as allError:
            browser.quit()
            return (True, CFnum, allError, False, fileFlag)

        except:
            continue


    process_steps = {
                        '050':steps.step90,
                        '090':steps.step140,
                        '140':steps.step999
                    }

    if not flag:
        browser.quit()
        return (True, CFnum,'This is not a valid complaint folder number', False, fileFlag)

    elif medical_event == 'Yes':
        browser.quit()
        return (True, CFnum,'Medical event is Yes. Cannot process', False, fileFlag)

    elif pREflag:
        browser.quit()
        return (True, CFnum,'pRE is YES. Cannot close', False, fileFlag)

    elif current_step == '999':
        print('IR still open in step {}'.format(IRstep))
        browser.quit()
        return (True, CFnum, 'Complaint folder already closed - step {}'.format(current_step), False, fileFlag)

    elif IR and IRstep != '999':
        print('IR still open in step {}'.format(IRstep))
        browser.quit()
        return (True, CFnum, 'IR still open in step {}'.format(IRstep), False, fileFlag)
    elif len(username) == 0 or len(RDPC) == 0  or len(productFormula) == 0:
        print('Complaint folder not processable. Kindly check RDPC or product records.')
        browser.quit()
        return (True, CFnum, 'Complaint folder not processable. Kindly check RDPC or product records.', False, fileFlag)
    else:
        try:
            if not IR and (productType == 'Patient Interface') and (RDPC == 'Suction - lack prior to laser fire'):
                if (serialNum[0] != '6'):
                    if current_step == '140':
                        CFnum, statusMsg, statusFlag = process_steps[current_step](browser, CFnum, RDPC=RDPC, productType=productType, productFormula=productFormula, serialNum=serialNum, username=username,IR=IR,IRnum=IRnum)
                    else:
                        CFnum, statusMsg, statusFlag = process_steps['090'](browser, CFnum, RDPC=RDPC, productType=productType, productFormula=productFormula, serialNum=serialNum, username=username,IR=IR,IRnum=IRnum)
                    
                    browser.quit()
                    return (True, CFnum, statusMsg, statusFlag, fileFlag)
                else:
                    browser.quit()
                    return (True, CFnum, 'Error! LOT number starts with 6 for PI return', False, fileFlag)   
            
            elif not IR and (RDPC == 'Failure to Capture' or RDPC == 'Loss of Capture') and (productFormula == 'LOI' or productFormula == '0180-1201' or productFormula == '0180-1401') \
            or ((RDPC == 'Fluid Catchment Filled') and (productFormula == 'LOI')):
                if current_step == '140':
                    CFnum, statusMsg, statusFlag = process_steps[current_step](browser, CFnum, RDPC=RDPC, productType=productType, productFormula=productFormula, serialNum=serialNum, username=username,IR=IR,IRnum=IRnum)
                else:
                    CFnum, statusMsg, statusFlag = process_steps['090'](browser, CFnum, RDPC=RDPC, productType=productType, productFormula=productFormula, serialNum=serialNum, username=username,IR=IR,IRnum=IRnum)
                
                browser.quit()
                return (True, CFnum, statusMsg, statusFlag, fileFlag) 
            else:
                print('Inside else part')
                CFnum, statusMsg, statusFlag = process_steps[current_step](browser, CFnum, RDPC=RDPC, productType=productType, productFormula=productFormula, serialNum=serialNum, username=username,IR=IR,IRnum=IRnum)
                browser.quit()
                return (True, CFnum, statusMsg, False, fileFlag)
        except KeyError:
            print('Error! The current step is {}'.format(current_step))
            browser.quit()
            return (True, CFnum, 'Error! The current step is {}'.format(current_step), False, fileFlag)

        





    



    


