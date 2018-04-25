import os
import sys
import json
import ctypes
import shutil
import zipfile
import logging
import subprocess
from subprocess import PIPE
from distutils.version import LooseVersion
zipPath = os.path.abspath(os.environ.get('TEMP'))


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception as e:
        return False


def RunShell(packageName, command):
    try:
        p = subprocess.Popen(command, shell=True, stdout=PIPE, stderr=PIPE)
        stdout, stderr = p.communicate()
        if stderr:
            logging.info(str(packageName) + ' Update Error :')
            logging.info(stderr.decode('ascii'))
        if stdout:
            logging.info(str(packageName) + ' Update Success :')
            logging.info(stdout.decode('ascii'))

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        lineNo = str(exc_tb.tb_lineno)
        print('Error : %s : %s at Line %s.' % (type(e), e, lineNo))
        logging.info('Error : %s : %s at Line %s.' % (type(e), e, lineNo))


def FirstRun(jsonFile):
    if not os.path.exists(jsonFile):
        logging.info('LatestVersions.json doesnt exist. Creating file..')
        data = {"Opera": "1.11", "Chrome": "1.11", "Firefox": "0.11.1", "InternetExplorer": "1.1.0"}
        JsonWrite(jsonFile, data)
        InstallPackages()


def InstallPackages():
        # Install required packages
        packages = ['beautifulsoup4', 'requests']
        for packageName in packages:
            command = "pip install --upgrade " + packageName
            RunShell(packageName, command)


def JsonWrite(jsonFile, data):
    try:
        with open(jsonFile, 'w') as outfile:
            json.dump(data, outfile)
        logging.info('Successfully updated version info.')
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        lineNo = str(exc_tb.tb_lineno)
        logging.info('Error: %s : %s at Line %s.' % (type(e), e, lineNo))
        print('Error: %s : %s at Line %s.' % (type(e), e, lineNo))


def JsonRead(jsonFile):
    try:
        with open(jsonFile) as json_file:
            data = json.load(json_file)
            # print(data)
        logging.info('Successfully read version info.')
        return data
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        lineNo = str(exc_tb.tb_lineno)
        logging.info('Error: %s : %s at Line %s.' % (type(e), e, lineNo))
        print('Error: %s : %s at Line %s.' % (type(e), e, lineNo))


def DownloadFile(URL, filename=''):
    try:
        import requests
        if filename == '':
            filename = str(URL.split('/')[-1])

        r = requests.get(URL)
        with open(filename, 'wb') as code:
            code.write(r.content)
        print('Successfully downloaded %s' % filename)
        return filename

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        lineNo = str(exc_tb.tb_lineno)
        logging.info('Error: %s : %s at Line %s.' % (type(e), e, lineNo))
        print('Error: %s : %s at Line %s.' % (type(e), e, lineNo))
        return None


def GetWebPage(link):
    try:
        import requests, bs4
        session = requests.Session()
        resp = session.get(link)
        resp.raise_for_status()
        if resp.status_code != 200:
            raise IOError('Error connecting to %s ' % link)
            logging.error('Connetion Error')
            soup = None
            (version, downloadURL) = (None, None)
        else:
            soup = bs4.BeautifulSoup(resp.text, 'html.parser')
            # print(soup)
            if 'github.com' in link:
                GithubCss = '.release-title'
                elems = soup.select(GithubCss)
                version = elems[0].getText().strip()
                version = version.split('v')[-1]   # to remove the v from geckodriver
                contents = []
                driverURLs = soup.findAll('a', href=True)
                for driverURL in driverURLs:
                    if 'win32' in str(driverURL):
                        contents.append(driverURL)
                if len(contents) > 0:
                    downloadURL = contents[0].get('href')
                    downloadURL = 'https://github.com' + downloadURL
                else:
                    (version, downloadURL) = (None, None)

            elif 'google.com' in link:
                contents = []
                for string in (soup.findAll('a', href=True)):
                    if 'storage.googleapis.com/index.html' in str(string):
                        contents.append(string)
                if len(contents) > 0:
                    version = contents[0].getText().split()[1]
                    downloadURL = contents[0].get('href')
                else:
                    (version, downloadURL) = (None, None)

            elif 'seleniumhq.org' in link:
                content = []
                for items in soup.findAll('p'):
                    if '32 bit Windows IE' in str(items):
                        content.append(items)
                if len(content) > 0:
                    version = str(content[0].contents[0]).split()[2]
                    downloadURL = content[0].contents[1].get('href')
                else:
                    (version, downloadURL) = (None, None)
            else:
                (version, downloadURL) = (None, None)
        session.close
        return (version, downloadURL)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        lineNo = str(exc_tb.tb_lineno)
        logging.info('Error: %s : %s at Line %s.' % (type(e), e, lineNo))
        print('Error: %s : %s at Line %s.' % (type(e), e, lineNo))
        return (None, None)


def UnZip(zipFileName, unZipFolderPath):
    '''
    Function to Un-ZIP files. Returns True if Unzip completed; False if any error occured.
    '''
    try:
        with zipfile.ZipFile(zipFileName, "r") as zip_ref:
            zip_ref.extractall(unZipFolderPath)
        print('Unzipping %s Completed.' % zipFileName)
        return True
    except Exception as e:
        print('Error while UnZipping %s : %s' % (zipFileName, str(e)))
        return False


def main():
    logging.info('-----UpdateDriver Script Run Begin---')

    PathVariables = os.environ.get('PATH')
    for Path in PathVariables.split(';'):
        if ('Python' in Path) and ('Scripts' in Path):
            DriverPath = Path
            break

    if not DriverPath:
        DriverPath = 'C:\\Windows'

    if not os.path.exists(DriverPath):
        os.makedirs(DriverPath, exist_ok=True)
    jsonFile = os.path.join(DriverPath, 'LatestVersions.json')

    Ie11URL = 'http://www.seleniumhq.org/download/'
    ChromeURL = 'https://sites.google.com/a/chromium.org/chromedriver/downloads'
    OperaURL = 'https://github.com/operasoftware/operachromiumdriver/releases'
    FirefoxURL = 'https://github.com/mozilla/geckodriver/releases'

    log_file_path = os.path.join(DriverPath, "SeleniumDrivers.log")
    logging.basicConfig(level=logging.INFO,
                        filename=log_file_path,
                        format='%(asctime)s    : %(message)s')
    # logging.disable(logging.CRITICAL)

    FirstRun(jsonFile)
    os.chdir(zipPath)
    data = JsonRead(jsonFile)
    IENewVersion, IEDriverURL = GetWebPage(Ie11URL)
    if IEDriverURL is not None:
        logging.info(IENewVersion + ' - ' + IEDriverURL)
        IEOldVersion = data.get('InternetExplorer')
        logging.info('%s - Current Version of IE11 Selenium driver' % IEOldVersion)
        if LooseVersion(IEOldVersion) < LooseVersion(IENewVersion):
            print('%s -  IE11 Latest driver version' % IENewVersion)
            logging.info('%s -  IE11 Latest driver version' % IENewVersion)
            zipFileName = DownloadFile(IEDriverURL, filename=('IEDriver_Win32_' + IENewVersion + '.zip'))
            if zipFileName is not None:
                logging.info('Successfully downloaded %s' % zipFileName)
                if UnZip(zipFileName, DriverPath):
                    data['InternetExplorer'] = IENewVersion
                    logging.info('%s File UnZipped Successfully.' % zipFileName)
                    JsonWrite(jsonFile, data)
        else:
            logging.info('%s - Already Up to date IE11  driver version' % IENewVersion)
            print('%s - Already Up to date IE11  driver version' % IENewVersion)

    OperaNewVersion, OperaDriverURL = GetWebPage(OperaURL)
    if OperaDriverURL is not None:
        logging.info(OperaNewVersion + ' - ' + OperaDriverURL)
        OperaOldVersion = data.get('Opera')
        logging.info('%s - Current Version of Opera Selenium driver' % OperaOldVersion)
        if LooseVersion(OperaOldVersion) < LooseVersion(OperaNewVersion):
            print('%s -  Opera Latest driver version' % OperaNewVersion)
            logging.info('%s -  Opera Latest driver version' % OperaNewVersion)
            zipFileName = DownloadFile(OperaDriverURL)
            if zipFileName is not None:
                logging.info('Successfully downloaded %s' % zipFileName)
                if UnZip(zipFileName, DriverPath):
                    data['Opera'] = OperaNewVersion
                    logging.info('%s File UnZipped Successfully.' % zipFileName)
                    JsonWrite(jsonFile, data)
        else:
            logging.info('%s - Already Up to date Opera driver version' % OperaNewVersion)
            print('%s - Already Up to date Opera driver version' % OperaNewVersion)
        if os.path.exists(DriverPath + '\\operadriver_win32\\operadriver.exe'):
            shutil.copy2(DriverPath + '\\operadriver_win32\\operadriver.exe', DriverPath)
        if os.path.exists(DriverPath + '\\operadriver.exe'):
            shutil.rmtree(DriverPath + '\\operadriver_win32', ignore_errors=True)

    FfoxNewVersion, FfoxDriverURL = GetWebPage(FirefoxURL)
    if FfoxDriverURL is not None:
        logging.info(FfoxNewVersion + ' - ' + FfoxDriverURL)
        FfoxOldVersion = data.get('Firefox')
        logging.info('%s - Current Version of Firefox Selenium driver' % FfoxOldVersion)
        if LooseVersion(FfoxOldVersion) < LooseVersion(FfoxNewVersion):
            print('%s -  Firefox Latest driver version' % FfoxNewVersion)
            logging.info('%s -  Firefox Latest driver version' % FfoxNewVersion)
            zipFileName = DownloadFile(FfoxDriverURL)
            if zipFileName is not None:
                logging.info('Successfully downloaded %s' % zipFileName)
                if UnZip(zipFileName, DriverPath):
                    data['Firefox'] = FfoxNewVersion
                    logging.info('%s File UnZipped Successfully.' % zipFileName)
                    JsonWrite(jsonFile, data)
        else:
            logging.info('%s - Already Up to date Firefox driver version' % FfoxNewVersion)
            print('%s - Already Up to date Firefox driver version' % FfoxNewVersion)

    ChromeNewVersion, ChromeDriverlink = GetWebPage(ChromeURL)
    if ChromeDriverlink is not None:
        logging.info(ChromeNewVersion + ' - ' + ChromeDriverlink)
        ChromeOldVersion = data.get('Chrome')
        logging.info('%s - Current Version of Chrome Selenium driver' % ChromeOldVersion)
        if LooseVersion(ChromeOldVersion) < LooseVersion(ChromeNewVersion):
            print('%s -  Chrome Latest driver version' % ChromeNewVersion)
            logging.info('%s -  Chrome Latest driver version' % ChromeNewVersion)
            ChromeDriverURL = 'https://chromedriver.storage.googleapis.com/' + ChromeNewVersion + '/chromedriver_win32.zip'
            zipFileName = DownloadFile(ChromeDriverURL)
            if zipFileName is not None:
                logging.info('Successfully downloaded %s' % zipFileName)
                if UnZip(zipFileName, DriverPath):
                    data['Chrome'] = ChromeNewVersion
                    logging.info('%s File UnZipped Successfully.' % zipFileName)
                    JsonWrite(jsonFile, data)
        else:
            logging.info('%s - Already Up to date Chrome driver version' % ChromeNewVersion)
            print('%s - Already Up to date Chrome driver version' % ChromeNewVersion)

    logging.info('-----UpdateDriver Script Run Ended---\n')


def bootstrap():
    try:
        import bs4
        import requests
    except:
        InstallPackages()

    if is_admin():
        main()
    else:
        print('Admin access required to run this script.')


if __name__ == '__main__':
    bootstrap()
