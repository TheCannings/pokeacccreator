from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.ui import Select
from random import randint
from seleniumrequests import PhantomJS
import random
import string
import time
import urllib2
import logging
import datetime
import requests
import yaml
import os

__all__ = [
    'PTCException',
    'PTCInvalidStatusCodeException',
    'PTCInvalidNameException',
    'PTCInvalidEmailException',
    'PTCInvalidPasswordException',
    'PTCInvalidBirthdayException',
    'PTCTwocaptchaException',
    'PTCRateLimitExceeded'
]


class PTCException(Exception):
    """Base exception for all PTC Account exceptions"""
    pass


class PTCInvalidStatusCodeException(Exception):
    """Base exception for all PTC Account exceptions"""
    pass


class PTCInvalidNameException(PTCException):
    """Username already in use"""
    pass


class PTCInvalidEmailException(PTCException):
    """Email invalid or already in use"""
    pass


class PTCInvalidPasswordException(PTCException):
    """Password invalid"""
    pass


class PTCInvalidBirthdayException(PTCException):
    """Birthday invalid"""
    pass


class PTCTwocaptchaException(PTCException):
    """2captcha unable to provide service"""
    pass


class PTCRateLimitExceeded(PTCException):
    """Rate limit exceeded"""
    pass


def openurl(address):
    try:
        urlresponse = urllib2.urlopen(address).read()
        return urlresponse
    except urllib2.HTTPError, e:
        print("HTTPError = " + str(e.code))
    except urllib2.URLError, e:
        print("URLError = " + str(e.code))
    except Exception:
        import traceback
        print("Generic Exception: " + traceback.format_exc())
    print("Request to " + address + "failed.")
    return "Failed"


def activateurl(address):
    try:
        urlresponse = urllib2.urlopen(address)
        return urlresponse
    except urllib2.HTTPError, e:
        print("HTTPError = " + str(e.code))
    except urllib2.URLError, e:
        print("URLError = " + str(e.code))
    except Exception:
        import traceback
        print("Generic Exception: " + traceback.format_exc())
    print("Request to " + address + "failed.")
    return "Failed"


def autocaptcha(captchakey2, driver):
    captchatimeout = 2000
    # Now to automatically handle captcha
    html_source = driver.page_source
    gkey_index = html_source.find("https://www.google.com/recaptcha/api2/anchor?k=") + 47
    gkey = html_source[gkey_index:gkey_index + 40]
    recaptcharesponse = "Failed"
    while (recaptcharesponse == "Failed"):
        recaptcharesponse = openurl("http://2captcha.com/in.php?key=" + captchakey2 + "&method=userrecaptcha&googlekey=" + gkey + "&pageurl=" + driver.current_url)
    captchaid = recaptcharesponse[3:]
    recaptcharesponse = "CAPCHA_NOT_READY"
    elem = driver.find_element_by_class_name("g-recaptcha")
    start_time = int(time.time())
    timedout = False
    while recaptcharesponse == "CAPCHA_NOT_READY":
        time.sleep(10)
        elapsedtime = int(time.time()) - start_time
        if elapsedtime > captchatimeout:
            logging.info("Captcha timeout reached. Exiting.")
            timedout = True
            break
        recaptcharesponse = "Failed"
        while (recaptcharesponse == "Failed"):
            recaptcharesponse = openurl(
                "http://2captcha.com/res.php?key=" + captchakey2 + "&action=get&id=" + captchaid)
    if timedout == False:
        solvedcaptcha = recaptcharesponse[3:]
        captchalen = len(solvedcaptcha)
        elem = driver.find_element_by_name("g-recaptcha-response")
        elem = driver.execute_script("arguments[0].style.display = 'block'; return arguments[0];", elem)
        elem.send_keys(solvedcaptcha)
        logging.info("Solved captcha")


def mainprocess(captchakey, saveloc):
    user_agent = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_4) " + "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/29.0.1547.57 Safari/537.36")

    dcap = dict(DesiredCapabilities.PHANTOMJS)
    dcap["phantomjs.page.settings.userAgent"] = user_agent
    driver = PhantomJS(desired_capabilities=dcap, service_args=['--load-images=no'])

    #driver = webdriver.PhantomJS()
    driver.set_window_size(1600, 1200)
    driver.implicitly_wait(10)

    driver.get("https://club.pokemon.com/us/pokemon-trainer-club")
    driver.find_element_by_id("user-account-signup").click()

    delay = 5  # seconds
    try:
        myElem = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.ID, 'id_dob')))
    except TimeoutException:
        logging.info("Loading took too much time!")

    elem = driver.find_element_by_name("dob") 

    driver.execute_script("var input = document.createElement('input'); input.type='text'; input.setAttribute('name', 'dob'); arguments[0].parentNode.replaceChild(input, arguments[0])", elem)

    randdate=datetime.date(randint(1975,1990), randint(1,12),randint(1,28))

    elem = driver.find_element_by_name("dob") 
    elem.send_keys(datetime.datetime.strftime(randdate, '%Y-%m-%d'))  

    driver.save_screenshot('bday4.png')  

    time.sleep(1)

    delay = 5  # seconds
    try:
        myElem = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.XPATH, '//*[@id="sign-up-theme"]/section/div/div/div[1]/form/div[2]/div/div/label')))
    except TimeoutException:
        logging.info("Loading took too much time!")

    myElem.click()

    time.sleep(1)

    delay = 5  # seconds
    try:
        myElem = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.XPATH, '//*[@id="sign-up-theme"]/section/div/div/div[1]/form/div[2]/div/div/div/div/ul/li[168]')))
    except TimeoutException:
        logging.info("Loading took too much time!")

    myElem.click()

    driver.find_element_by_xpath('//*[@id="sign-up-theme"]/section/div/div/div[1]/form/input[2]').click()

    randomemail = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))
    randompass = ''.join(random.SystemRandom().choice(string.ascii_lowercase + string.ascii_uppercase + string.digits + string.punctuation) for _ in range(10))

    driver2 = PhantomJS(desired_capabilities=dcap, service_args=['--load-images=no'])
    driver2.set_window_size(1600, 1200)

    driver2.get("https://temp-mail.org/en/option/change/")

    driver2.find_element_by_name("mail").send_keys(randomemail)

    doms = Select(driver2.find_element_by_xpath('//*[@id="domain"]'))

    x = doms.options

    domain = str(x[0].text)

    time.sleep(3)

    driver2.find_element_by_id('postbut').click()

    driver2.get("https://temp-mail.org/en/option/refresh/")

    driver.save_screenshot('screenshot.png')

    driver.find_element_by_id('id_username').send_keys(randomemail)

    driver.find_element_by_id('check-availability-username').click()

    delay = 5  # seconds
    try:
        myElem = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.XPATH, '//*[@id="username-suggestion"]/div/h3')))
        if driver.find_element_by_xpath('//*[@id="username-suggestion"]/div').find_element_by_tag_name('h3').text == 'Username is invalid.':
            logging.info('Username already in use exiting')
            exit()
    except TimeoutException:
        logging.info("Loading took too much time!")

    driver.find_element_by_id('id_password').send_keys(randompass)

    driver.find_element_by_id('id_confirm_password').send_keys(randompass)

    driver.find_element_by_id('id_email').send_keys(randomemail + domain)

    driver.find_element_by_id('id_confirm_email').send_keys(randomemail + domain)

    driver.find_element_by_id('id_screen_name').send_keys(randomemail)

    driver.find_element_by_id('check-availability-screen-name').click()

    delay = 5  # seconds
    try:
        myElem = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.XPATH, '//*[@id="user-signup-create-account-form"]/fieldset[1]/div/div/div[1]/div/div[11]/div/div/h3')))
        if driver.find_element_by_xpath('//*[@id="user-signup-create-account-form"]/fieldset[1]/div/div/div[1]/div/div[11]/div/div').find_element_by_tag_name('h3').text == 'This screen name already exists. Please try the following:':
            logging.info('Screen Name already in use exiting')
            exit()
    except TimeoutException:
        logging.info("Loading took too much time!")

    driver.find_element_by_id('id_terms').click()

    logging.info("Starting captcha solve")

    # AutoCapcha
    autocaptcha(captchakey, driver)

    driver.find_element_by_xpath('//*[@id="user-signup-create-account-form"]/fieldset[2]/div/input').click()

    driver.close()

    logging.info("Waiting on Email")

    for z in range(0, 5):
        try:
            delay = 60  # seconds
            try:
                myElem = WebDriverWait(driver2, delay).until(EC.presence_of_element_located((By.XPATH, '//*[@id="mails"]/tbody/tr/td[1]/a')))
            except TimeoutException:
                driver2.refresh()
        except:
            if z == 4:
                logging.info("Can't Find the email sorries :(")
            continue

    myElem.click()

    time.sleep(5)

    elems = driver2.find_elements_by_tag_name('a')
    time.sleep(5)
    for elem in elems:
        test = str(elem.get_attribute("href"))
        if "https://club.pokemon.com/us/pokemon-trainer-club/activated/" in test:
            actions = ActionChains(driver2)
            actions.move_to_element(elem).perform()
            elem.click()
            break

    time.sleep(10)

    driver2.quit()

    logging.info("Account created saving details")

    with open(os.path.join(saveloc, 'accounts.txt', "a")) as myfile:
        myfile.write("\n" + randomemail + ' - ' + randompass)

    logging.info(randomemail + " account created")

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M',
                    filename='myapp.log',
                    filemode='w')

# define a Handler which writes INFO messages or higher to the sys.stderr
console = logging.StreamHandler()
console.setLevel(logging.INFO)
# set a format which is simpler for console use
formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
# tell the handler to use this format
console.setFormatter(formatter)
# add the handler to the root logger
logging.getLogger('').addHandler(console)

cwd = os.getcwd()

if not os.path.isfile(os.path.join(cwd, 'config.yml')):
    print('No config file exists please edit the config.yml.example and input your 2captcha key')
    quit()
else:
    with open("config.yml", 'r') as ymlfile:
        cfg = yaml.load(ymlfile)

captchakey = cfg['2captcha']['key']
saveloc = cfg['savelocation']['directory']

if captchakey == '' or saveloc == '':
    print('Please enter your 2captchakey and save location into the config file')
elif not os.path.isdir(saveloc):
    createdirector = raw_input("Directory does not exist would you like it created? \n")

    if str(createdirector).upper() == 'Y':
        os.makedirs(saveloc)
    else:
        print('Cannot continue without directory exiting')
        quit()

accountnum = 0
accountnum = raw_input("How many accounts would you like to make? \n")

logging.info("Creating " + str(accountnum) + " Accounts")

for x in range(1, int(accountnum) + 1):
    try:
        logging.info("Starting Account number " + str(x) + "/" + str(accountnum))
        mainprocess(captchakey, saveloc)
    except Exception as e:
        logging.info(e)
        continue
