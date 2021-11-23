import os
import re
import time
import requests
from bs4 import BeautifulSoup
import smtplib, ssl
import config
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from selenium import webdriver
from selenium.webdriver.support.select import Select
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.firefox.options import Options as FirefoxOptions

start = time.time()
start_tuple=time.localtime()
start_time = time.strftime("%Y-%m-%d %H:%M:%S", start_tuple)

def write_to_file(the_list):
    with open(config.file_path+'unique.txt', 'w') as f:
        for elem in the_list: 
            f.write(str(elem[0]) + '\n')
    f.close()

path=config.driver_path
options = FirefoxOptions()
options.add_argument("--headless")
driver = webdriver.Firefox(options=options, executable_path=config.driver_path)
# driver = webdriver.Firefox(executable_path=config.driver_path)
models = ['VOLKSWAGEN_GOLF%207', 'SKODA_SUPERB', 'SKODA_OCTAVIA']
bodyTypes='Wagon'
fuelTypes='Diesel'
driveTypes='FWD'
priceTo='12000'
pageSize='100'
the_list=[]
for i in range(0, len(models)):
    page = f'https://longo.lv/automasinu-katalogs?models={models[i]}&bodyTypes={bodyTypes}&fuelTypes={fuelTypes}&driveTypes={driveTypes}&priceTo={priceTo}&pageSize={pageSize}'
    # print(page)
    driver.get(page)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(1) # Let the user actually see something!
    divs=driver.find_elements_by_class_name('col-6.col-md-4')
    for div in divs:
        if "lietoti" in div.find_element_by_tag_name('a').get_attribute('href'):
            links=div.find_element_by_tag_name('a').get_attribute('href')
            for el in (div.find_elements_by_class_name('v-card-item__content')):
                title=el.find_element_by_class_name('v-card-item__title').text
                for el2 in (el.find_elements_by_class_name('v-card-item__full-price')):
                    price=el2.find_element_by_class_name('v-card-item__price-value').text
            for el3 in (div.find_elements_by_class_name('v-card-item__content')):
                for el4 in (el3.find_elements_by_class_name('v-card-item__details')):
                    if len(el4.find_elements_by_class_name('chip')) == 3:
                        milage=el4.find_elements_by_class_name('chip')[0].text
                        fuel=el4.find_elements_by_class_name('chip')[1].text
                        transmission=el4.find_elements_by_class_name('chip')[2].text
            the_list.append([links,title,price,milage,fuel,transmission])
        else:
            continue
driver.close()

# write_to_file(the_list)


test = [i[0] for i in the_list]
file_text=open(config.file_path+'unique.txt', 'r').read().split('\n')
diff=[line for line in test if line not in file_text]
while True:
    if len(diff) == 0:
        break
    if len(diff) > 0:
        os.remove(config.file_path+"unique.txt")
        write_to_file(the_list)
        HTML_text = []
        for i in range(0, len(diff)):
            for n in range(0, len(the_list)):
                if the_list[n][0] == diff[i]:
                    HTML_text.append(str("<tr><td><a href='"+the_list[n][0]+"'>"+the_list[n][1]+"</a></td><td>"+the_list[n][2]+"</td><td>"+the_list[n][3]+"</td><td>"+the_list[n][4]+"</td><td>"+the_list[n][5]+"</td></tr>"))
        sender_email = config.sender_email
        receiver_email = config.receiver_email
        password = config.password
        message = MIMEMultipart("alternative")
        timestr = time.strftime("%d.%m.%Y-%H:%M:%S")
        message["Subject"] = "LONGO "+timestr 
        message["From"] = sender_email
        message["To"] = receiver_email
        epasta_saturs="\n".join([(str(i).replace('\n', '')) for i in diff])
        plain=f"""{epasta_saturs}"""
        html = f"""\
        <html>
        <body>
            <table border='1' style='border-collapse:collapse'>
                <tr>
                    <th>Title</th>
                    <th>Price</th>
                    <th>Milage</th>
                    <th>Fuel</th>
                    <th>Transmission</th>
                </tr>
                {" ".join(str(x) for x in HTML_text)}
            </table>
        </body>
        </html>
        """
        # print(html)
        part1 = MIMEText(plain, "plain")
        part2 = MIMEText(html, "html")
        message.attach(part1)
        message.attach(part2)
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(sender_email, password)
            server.sendmail(
                sender_email, receiver_email, message.as_string()
            )
        break

end = time.time()
end_tuple = time.localtime()
end_time = time.strftime("%Y-%m-%d %H:%M:%S", end_tuple)
print("Script ended: "+end_time)
print("Script running time: "+time.strftime('%H:%M:%S', time.gmtime(end - start)))

