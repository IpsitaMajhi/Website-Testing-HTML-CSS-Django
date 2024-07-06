from django.shortcuts import render
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from faker import Faker
from random import randint
import csv
import time
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import ActionChains
import datetime
import requests
import subprocess
import json
from bs4 import BeautifulSoup
from matplotlib import pyplot as plt
import logging
import os
import psutil
import requests
import subprocess
import webbrowser
from scapy.all import sniff,TCP
import socket
import ssl

def check_clickable_items(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error accessing {url}: {e}")
        return [{"error": f"Error accessing {url}: {e}"}], []
    soup = BeautifulSoup(response.text, 'html.parser')
    buttons = soup.find_all('button')
    anchors = soup.find_all('a', href=True)
    button_report = check_buttons(url, buttons)
    clickable_report = check_anchors(url, anchors)
    return button_report, clickable_report


def check_buttons(url, buttons):
    button_report = []
    serial_number = 1
    for button in buttons:
        button_text = button.get_text(strip=True)
        onclick = button.get('onclick')
        link_url = None
        new_window = False
        status_code = None
        error_message = None
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if onclick and onclick.startswith('window.location.href='):
            link_url = onclick.split('=')[1].strip('"\'')
            if not link_url.startswith(('http', 'https')):
                link_url = requests.compat.urljoin(url, link_url)
            try:
                link_response = requests.get(link_url)
                status_code = link_response.status_code
                if status_code != 200:
                    error_message = f"Button leading to {link_url} returned status code {status_code}"
            except requests.RequestException as e:
                status_code = 'Error'
                error_message = f"Error accessing {link_url}: {e}"
        elif onclick and onclick.startswith('window.open('):
            new_window = True
            link_url = onclick.split('(')[1].split(',')[0].strip('"\'')
            if not link_url.startswith(('http', 'https')):
                link_url = requests.compat.urljoin(url, link_url)
            try:
                link_response = requests.get(link_url)
                status_code = link_response.status_code
                if status_code != 200:
                    error_message = f"Button leading to {link_url} returned status code {status_code}"
            except requests.RequestException as e:
                status_code = 'Error'
                error_message = f"Error accessing {link_url}: {e}"
        else:
            error_message = "Button does not have a valid 'onclick' attribute."
        button_report.append({
            'serial_number': serial_number,
            'element_type': 'button',
            'element_text': button_text,
            'link_url': link_url,
            'status_code': status_code,
            'timestamp': timestamp,
            'new_window': new_window,
            'error_message': error_message
        })
        serial_number += 1
    return button_report


def check_anchors(url, anchors):
    clickable_report = []
    serial_number = 1
    for anchor in anchors:
        anchor_text = anchor.get_text(strip=True)
        href = anchor['href']
        new_window = anchor.get('target') == '_blank'
        status_code = None
        error_message = None
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if href:
            link_url = href
            if not link_url.startswith(('http', 'https')):
                link_url = requests.compat.urljoin(url, link_url)
            try:
                link_response = requests.get(link_url)
                status_code = link_response.status_code
                if status_code != 200:
                    error_message = f"Anchor leading to {link_url} returned status code {status_code}"
            except requests.RequestException as e:
                status_code = 'Error'
                error_message = f"Error accessing {link_url}: {e}"
        else:
            error_message = "Anchor does not have a valid 'href' attribute."
        clickable_report.append({
            'serial_number': serial_number,
            'element_type': 'anchor',
            'element_text': anchor_text,
            'link_url': link_url,
            'status_code': status_code,
            'timestamp': timestamp,
            'new_window': new_window,
            'error_message': error_message
        })
        serial_number += 1
    return clickable_report


def check_images(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error accessing {url}: {e}")
        return [{"error": f"Error accessing {url}: {e}"}]

    soup = BeautifulSoup(response.text, 'html.parser')
    images = soup.find_all('img')

    image_report = []

    for index, img in enumerate(images, start=1):
        src = img.get('src')
        if src:
            if not src.startswith(('http', 'https')):
                src = requests.compat.urljoin(url, src)
            try:
                img_response = requests.get(src)
                img_status = img_response.status_code
                if img_status == 200:
                    image_report.append({
                        'serial_number': index,
                        'src': src,
                        'status': 'Loaded successfully'
                    })
                else:
                    image_report.append({
                        'serial_number': index,
                        'src': src,
                        'status': f'Failed to load, status code: {img_status}'
                    })
            except requests.RequestException as e:
                image_report.append({
                    'serial_number': index,
                    'src': src,
                    'status': f'Failed to load: {e}'
                })
        else:
            image_report.append({
                'serial_number': index,
                'src': 'N/A',
                'status': 'No src attribute found'
            })

    return image_report


def main():
    url = "https://www.bourntec.com/"

    print("Checking URL:", url)
    with open(f"1.csv", "a") as fp:
        # fp.writelines(f'\t\t\n---------------------------\n')
       # fp.writelines(f'\t\ Testing Url  {url}\n')
        fp.writelines(f'\t\t---------------------------\n')
    button_report, clickable_report = check_clickable_items(url)
    image_report = check_images(url)

    result = {
        'url': url,
        'button_report': button_report,
        'clickable_report': clickable_report,
        'image_report': image_report
    }

    print(json.dumps(result, indent=4))
    with open(f"1.csv", "a") as fp:
        fp.writelines(f'\t\t\n---------------------------\n')
        fp.writelines(f'\t\t{json.dumps(result, indent=4)}\n')
        fp.writelines(f'\t\t---------------------------\n')

# Configure logging
logging.basicConfig(level=logging.INFO, filename='1.csv', filemode='a', format='%(asctime)s - %(levelname)s - %(message)s')

# Configure logging
logging.basicConfig(level=logging.INFO, filename='1.csv', filemode='a', format='%(asctime)s - %(levelname)s - %(message)s')

# Asset Management: Inventory assets
def inventory_assets():
    logging.info("Inventorying hardware and software assets...")
    hardware_assets = []
    for proc in psutil.process_iter(['pid', 'name']):
        hardware_assets.append(proc.info)
    logging.info(f"Hardware Assets: {hardware_assets}")
    return hardware_assets

# Access Control: Check open ports using psutil
def check_open_ports():
    logging.info("Checking open ports...")
    open_ports = []
    for conn in psutil.net_connections(kind='inet'):
        if conn.status == psutil.CONN_LISTEN:
            open_ports.append(conn.laddr.port)
    logging.info(f"Open Ports: {open_ports}")
    return open_ports

# Data Protection: Check for encryption
def check_encryption(url):
    logging.info(f"Checking encryption for {url}...")
    try:
        response = requests.get(url)
        if response.url.startswith('https'):
            logging.info(f"Connection to {url} is encrypted.")
            return f"Connection to {url} is encrypted."
        else:
            logging.warning(f"Connection to {url} is not encrypted.")
            return f"Connection to {url} is not encrypted."
    except requests.RequestException as e:
        logging.error(f"An error occurred while checking encryption for {url}: {e}")
        return f"An error occurred while checking encryption for {url}: {e}"

# Incident Detection: Monitor network traffic
def monitor_traffic():
    logging.info("Monitoring network traffic...")
    packets = []

    def packet_callback(packet):
        if packet.haslayer(TCP) and packet[TCP].payload:
            payload = packet[TCP].payload
            logging.info(f"Payload: {payload}")
            packets.append(payload)

    sniff(filter="tcp", prn=packet_callback, store=0, timeout=10)
    return packets

# SSL Certificate Check
def check_ssl_certificate(hostname):
    try:
        ip_address = socket.gethostbyname(hostname)
        context = ssl.create_default_context()
        with socket.create_connection((ip_address, 443), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()
                if cert:
                    logging.info(f"SSL certificate found for {hostname}")
                    return True
                else:
                    logging.warning(f"No SSL certificate found for {hostname}")
                    return False
    except socket.gaierror as e:
        logging.error(f"DNS resolution error: {e}")
        return False
    except ssl.SSLError as e:
        logging.error(f"SSL error: {e}")
        return False
    except Exception as e:
        logging.error(f"Error checking SSL certificate: {e}")
        return False

# Generate report
def generate_report(report_data, file_name="1.csv"):
    try:
        with open(file_name, "a") as report_file:
            for key, value in report_data.items():
                report_file.write(f"{key}:\n")
                if isinstance(value, list):
                    for item in value:
                        report_file.write(f"  - {item}\n")
                else:
                    report_file.write(f"  {value}\n")
                report_file.write("\n")
        logging.info(f"Report generated successfully: {file_name}")
    except Exception as e:
        logging.error(f"Failed to generate report: {e}")

# Main function to run all checks and generate a report
def run_security_checks():
    url = "https://www.bourntec.com/"
    webbrowser.open(url)

    report_data = {}
    report_data["Hardware Assets"] = inventory_assets()
    report_data["Open Ports"] = check_open_ports()
    report_data["Encryption Check"] = check_encryption(url)
    report_data["SSL Certificate Check"] = check_ssl_certificate("www.bourntec.com")
    report_data["Network Traffic"] = monitor_traffic()

    generate_report(report_data)


def count_words(text):
    return len(text.split())
def mobile_number():
    first_num = randint(6, 9)
    mob = str(first_num)
    for _ in range(9):
        last_num = randint(0, 9)
        mob += str(last_num)
    return mob
def about_us(driver):
    with open(f"1.csv", "a") as fp:
        fp.writelines(f'\t\t---------------------------------------------------------\n')
        fp.writelines(f'\t\t Burger Button Test Started \n')
        fp.writelines(f'\t\t---------------------------------------------------------\n')
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    element = driver.find_element(By.XPATH, "//a[@id='meniicon']")
    achains = ActionChains(driver)
    achains.move_to_element(element).click().perform()
    time.sleep(1)

def loop(driver, lst):
        s = 0
        for j in lst:
            driver.find_element(By.XPATH, str(j)).click()
            driver.save_screenshot(f"{s}.png")
            s += 1
            with open(f"1.csv", "a") as fp:
                fp.writelines(f'\t\t Burger Button Details \n')
                fp.writelines(f'\t\t---------------------------------------------------------\n')
                fp.writelines(f'XPATH : {s} : {str(j)} TESTED\n')

            if s == 5:
                with open(f"1.csv", "a") as fp:
                    fp.writelines(f'\t\t---------------------------------------------------------\n')
                    fp.writelines(f'\t\t Burger Button Test Completed \n')
                    fp.writelines(f'\t\t---------------------------------------------------------\n')
                break
            else:
                common(driver)

def common(driver):

    lst = ["//a[@title='History & Culture']", "//a[@title='Accreditations & Certifications']",
               "//a[@title='Alliances & Partnership']", "//a[@title='Contact Us']", "//a[@title='Join Us']"]

    about_us(driver)
    about_uss = driver.find_element(By.XPATH, "//a[@title='About Us']")
    about_us_url = driver.current_url
    achains = ActionChains(driver)
    achains.move_to_element(about_uss).perform()



def generate_fake_data():
    fake = Faker()
    fname = fake.first_name()
    lname = fake.last_name()
    email = fake.email()
    mob = mobile_number()
    return [fname, lname, email, mob, "Tested By Selenium Automated Testing Tool"]


mainlst = list()
sublst = generate_fake_data()
mainlst.append(sublst)


def start_driver():
    print("Starting WebDriver...")
    service = Service(r"C:\Users\KIIT\OneDrive\Documents\chromedriver-win64\chromedriver-win64\chromedriver.exe")
    driver = webdriver.Chrome(service=service)
    print("WebDriver started successfully.")
    return driver

def fill_form(driver, data,lst):
    with open(f"1.csv", "a") as fp:
        fp.writelines(f'\t\t\n---------------------------\n')
        fp.writelines(f'\t\tPerformance Testing Ended\n')
        fp.writelines(f'\t\t---------------------------\n')
    wait = WebDriverWait(driver, 20)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    print("Page Downed Successfully..")
    with open(f"1.csv", "a") as fp:
        fp.writelines(f'\t\t\n---------------------------\n')
        fp.writelines(f'\t\tChatBot Testing Started\n')
        fp.writelines(f'\t\t---------------------------\n')
    driver.find_element(By.ID ,'brn-chatbot').click()
    #driver.find_element("""//*[@id="brn-chatbot"]""").click()

    time.sleep(2)
    #driver.find_element("""/html/body/div[16]/div[1]/div/div[2]/div[2]/button[1]""").click()
    #time.sleep(2)

    driver.find_element(By.XPATH,"/html/body/div[17]/div[1]/div/div[2]/div[2]/button[1]").click()

    time.sleep(5)
    driver.find_element(By.XPATH ,"/html/body/div[17]/div[1]/div/div[4]/div[2]/button[3]").click()
    time.sleep(5)
    driver.find_element(By.XPATH ,"/html/body/div[17]/div[1]/div/div[6]/div[2]/button[4]").click()
    time.sleep(5)
    driver.find_element(By.XPATH ,"/html/body/div[17]/div[1]/div/div[8]/div[2]/button[1]").click()
    time.sleep(5)
    # driver.find_element(By.XPATH ,"/html/body/div[17]/div[1]/div/div[5]/div[2]/button[1]").click()
    # time.sleep(5)
    # driver.find_element(By.XPATH ,"/html/body/div[17]/div[1]/div/div[18]/div[2]/button").click()
    driver.find_element(By.ID ,'brn-chatbot').click()
    with open(f"1.doc", "a") as fp:
        fp.writelines(f'\t\t\n---------------------------\n')
        fp.writelines(f'\t\tChatBot Testing Ended\n')
        fp.writelines(f'\t\t---------------------------\n')
    time.sleep(5)
    # Interact with the first name field
    input_firstname = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@id='input-firstname']")))
    driver.execute_script("arguments[0].scrollIntoView();", input_firstname)
    input_firstname.send_keys(data[0])
    print(f"Entered First Name: {data[0]}")
    
    # Interact with the last name field
    input_lastname = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@id='input-lastname']")))
    input_lastname.send_keys(data[1])
    print(f"Entered Last Name: {data[1]}")
    
    # Interact with the email field
    input_email = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@id='input-email']")))
    input_email.send_keys(data[2])
    print(f"Entered Email: {data[2]}")
    
    # Interact with the phone field
    input_phone = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@id='input-phone']")))
    input_phone.send_keys(data[3])
    print(f"Entered Mobile Number: {data[3]}")
    
    # Interact with the enquiry field
    input_enquiry = wait.until(EC.element_to_be_clickable((By.XPATH, "//textarea[@id='input-enquiry']")))
    input_enquiry.send_keys(data[4])
    print("Entered Enquiry Text")
    
    # Submit the form
    contact_submit = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(),'Submit')]")))
    driver.save_screenshot("test.png")
    time.sleep(5)
    contact_submit.click()
    alert = wait.until(EC.alert_is_present())
    alert.accept()
    time.sleep(5)
    driver.save_screenshot("success.png")
    print("Form Submitted Successfully")
    with open(f"1.doc", "a") as fp:
        fp.writelines(f'\t\t---------------------------\n')
        fp.writelines(f'Get In To Toucn Form Tested Successfully..\n')
        fp.writelines(f'\t\t---------------------------\n')
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    print("Page Downed Successfully..")
    # time.sleep(5)
    # with open(f"1.doc", "a") as fp:
    #     fp.writelines(f'\t\t Search Bar Testing Started \n')
    #     fp.writelines(f'\t\t---------------------------------------------------------\n')
    # element = driver.find_element(By.XPATH, "//i[@class='fa fa-long-arrow-up']")
    # element.click()
    # print("Bottom Button Clicked...")
    # element = driver.find_element(By.ID, "website_search")
    # element.send_keys("ai")
    # with open(f"1.doc", "a") as fp:
    #     fp.writelines(f'\t\t Search Bar Value Sended AI \n')
    #     fp.writelines(f'\t\t---------------------------------------------------------\n')
    # element.send_keys(Keys.ENTER)
    # print("Search Bar Tested...")
    #with open(f"1.doc", "a") as fp:
    #    fp.writelines(f'\t\t Search Bar Testing Completed \n')
    #    fp.writelines(f'\t\t---------------------------------------------------------\n')
    print("Paragraph Test Start....")
    with open(f"1.doc", "a") as fp:
        fp.writelines(f'\t\t Paragraph Test Started \n')
        fp.writelines(f'\t\t---------------------------------------------------------\n')
    paragraphs = driver.find_elements(By.TAG_NAME, 'p')
    for index, paragraph in enumerate(paragraphs):
        text = paragraph.text
        word_count = count_words(text)
        if word_count <= 20 and word_count != 0:
            print(f'Paragraph {index + 1}: {word_count} words Healthy')
            with open(f"1.txt", "a") as fp:
                fp.writelines(f'Paragraph {index + 1}: {word_count} words Healthy\t{text}\n')
        else:
            print(f'Paragraph {index + 1}: {word_count} words Not Recommended')
            with open(f"1.doc", "a") as fp:
                fp.writelines(f'Paragraph {index + 1}: {word_count} words Not Recommended\t{text}\n')
    print("Paragraph Test Completed and Generate Report File Name 1.doc Verify!!")
    with open(f"1.doc", "a") as fp:
        fp.writelines(f'\t\t Paragraph Test Completed \n')
        fp.writelines(f'\t\t---------------------------------------------------------\n')
    common(driver)
    loop(driver, lst)
    common(driver)
    with open(f"1.doc", "a") as fp:
        fp.writelines(f'\t\t Link Test Started \n')
        fp.writelines(f'\t\t---------------------------------------------------------\n')
    main()
    with open(f"1.doc", "a") as fp:
        fp.writelines(f'\t\t Link Test Completed \n')
        fp.writelines(f'\t\t---------------------------------------------------------\n')
    with open(f"1.doc", "a") as fp:
        fp.writelines(f'\t\t Security Test Started \n')
        fp.writelines(f'\t\t---------------------------------------------------------\n')
    run_security_checks()
    with open(f"1.doc", "a") as fp:
        fp.writelines(f'\t\t Security Test Completed \n')
        fp.writelines(f'\t\t---------------------------------------------------------\n')

def save_to_csv(data):
    with open("Website_Testing.csv", "a", newline='') as fp:
        csv_data = csv.writer(fp)
        csv_data.writerows([data])
    print("Data Stored In Website_Testing.csv and Bourntec Website Database Successfully!!")
    with open(f"1.doc", "a") as fp:
        fp.writelines(f'\t\t Verify Get Into Touch form data on Website Database or Website_Testing.csv \n')

def locate_id(request):

    lst = ["//a[@title='History & Culture']", "//a[@title='Accreditations & Certifications']",
               "//a[@title='Alliances & Partnership']", "//a[@title='Contact Us']", "//a[@title='Join Us']"]

    if request.method == "POST":

        driver = None

        try:

            with open(f"1.doc", "a") as fp:
                fp.writelines(f'\t\t Website Load Testing Starts \n')
                fp.writelines(f'\t\t---------------------------------\n')

            start_date = datetime.datetime.now()
            start_time = time.time()
            print(start_time)
            print("Start Date Time : ", start_date)
            with open(f"1.doc", "a") as fp:
                fp.writelines(f'\t\t Status : Time Start at :  {start_date}||{start_time} \n')
                fp.writelines(f'\t\t---------------------------------------------------------\n')

            response = requests.get('https://bourntec.com')
            end_time = time.time()
            end_date = datetime.datetime.now()
            print(end_time)
            print("End Date Time : ", end_date)
            with open(f"1.csv", "a") as fp:
                fp.writelines(f'\t\t Status : Time Ended at :  {end_date}||{end_time} \n')
                fp.writelines(f'Difference Time{end_time - start_time}\n')
                fp.writelines(f'\t\t---------------------------------------------------------\n')
            print(f'Difference Time{end_time - start_time}')
            print("=" * 50)
            print("Status Code of Website Reponse : ", response.status_code)  # Prints the HTTP status code
            print("=" * 50)
            print(response.headers)  # Prints the headers
            print("=" * 50)
            print(response.url)  # Prints the final URL
            print("=" * 50)
            print(response.elapsed)  # Prints the time elapsed
            print("=" * 50)
            # url = "https://www.v2demo.bourntec.com/"
            # num_requests = 20
            #
            # # Variables to store results
            # response_times = []
            # total_successful_requests = 0
            # total_load_time = 0
            #
            # # Performing basic performance test
            # print("Performing basic performance test...")
            #
            # for _ in range(num_requests):
            #     start_time = time.time()
            #     response = requests.get(url)
            #     end_time = time.time()
            #
            #     response_time = end_time - start_time
            #     status_code = response.status_code
            #
            #     if status_code == 200:
            #         response_times.append(response_time)
            #         total_load_time += response_time
            #         total_successful_requests += 1
            #
            # if total_successful_requests > 0:
            #     min_response_time = min(response_times)
            #     max_response_time = max(response_times)
            #     average_response_time = sum(response_times) / total_successful_requests
            # else:
            #     min_response_time = 0
            #     max_response_time = 0
            #     average_response_time = 0
            #
            # success_rate = (total_successful_requests / num_requests) * 100
            #
            # # Creating the report
            # basic_report = {
            #     'min_response_time': min_response_time,
            #     'max_response_time': max_response_time,
            #     'average_response_time': average_response_time,
            #     'success_rate': success_rate,
            #     'total_load_time': total_load_time,
            #     'num_requests': num_requests,
            #     'response_times': response_times
            # }

            with open(f"1.csv", "a") as fp:
                fp.writelines(f'\t\t Status and Details \n')
                fp.writelines(f'\t\t---------------------------------------------------------\n')
                fp.writelines(f'Status Code : {response.status_code}\n')
                fp.writelines(f'Headers : {response.headers}\n')
                fp.writelines(f'Current Url : {response.url}\n')
                fp.writelines(f'Elapsed : {response.elapsed}\n')
                # fp.write(f"URL: {url}\n")
                # fp.write(f"Number of Requests: {num_requests}\n")
                # fp.write(f"Total Successful Requests: {total_successful_requests}\n")
                # fp.write(f"Success Rate: {success_rate:.2f}%\n")
                # fp.write(f"Total Load Time: {total_load_time:.4f} seconds\n")
                # fp.write(f"Minimum Response Time: {min_response_time:.4f} seconds\n")
                # fp.write(f"Maximum Response Time: {max_response_time:.4f} seconds\n")
                # fp.write(f"Average Response Time: {average_response_time:.4f} seconds\n\n")
                # fp.write("Detailed Response Times:\n")
                # fp.write("------------------------\n")
                # for i, response_time in enumerate(response_times, 1):
                #     fp.write(f"Request {i}: {response_time:.4f} seconds\n")

            driver = start_driver()
            driver.get("https://bourntec.com/#home-carousel")
            driver.maximize_window()
            fill_form(driver, sublst,lst)
            save_to_csv(sublst)


        except Exception as e:
            print(f"An error occurred: {e}")
            with open(f"1.csv", "a") as fp:
                fp.writelines(f'\t\t Errors : {e} \n')
                fp.writelines(f'\t\t---------------------------------------------------------\n')
            if driver:
                driver.save_screenshot("error.png")
        finally:
            if driver:
                time.sleep(10)
                driver.quit()
                print("WebDriver closed.")
        return render(request, 'websitetestingtoolapp/home.html')

    return render(request, 'websitetestingtoolapp/home.html')

# def home_page_view(request):
#     return render(request,'websitetestingtoolapp/home.html')

