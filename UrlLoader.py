# 최종 리눅스 전용 URL loader + Selenium 
import os
import re
import hashlib
import requests
import time
import random
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from requests.exceptions import RequestException
from selenium_stealth import stealth
from webdriver_manager.chrome import ChromeDriverManager

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.1 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) Gecko/20100101 Firefox/115.0",
    "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:91.0) Gecko/20100101 Firefox/91.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/112.0.5615.49 Safari/537.36"

    # 새로 추가된 10개
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.6261.94 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.6167.139 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 13; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.6167.101 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:122.0) Gecko/20100101 Firefox/122.0",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 12_6_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Safari/605.1.15",
    "Mozilla/5.0 (Linux; Android 12; Pixel 6 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.129 Mobile Safari/537.36",
    "Mozilla/5.0 (iPad; CPU OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1"
]

class MakeFileByUrl:
    def __init__(self):
        self.driver = None
        self.base_url = ''
        self.folder_name = ''
        self.SAVE_DIR = ''
        self.html = ''
        self.soup = None
        self.downloaded = set()
        self.js_list = []

    def _setup_driver(self):
        '''headless 서버로 봇 탐지 우회 세팅'''
        options = Options()
        options.add_argument("--headless=new")
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-blink-features=AutomationControlled')
        
        # selenium stealth option 추가
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)

        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )
        stealth(self.driver,
                languages=["en-US", "en"],
                vendor="Google Inc.",
                platform="Win32",
                webgl_vendor="Intel Inc.",
                renderer="Intel Iris OpenGL Engine",
                fix_hairline=True)

    def get_url(self):
        '''올바른 형식의 url 검사'''
        while True:
            self.base_url = input("\nURL 입력 (https:// 포함): ").strip()
            parsed = urlparse(self.base_url)
            
            if not parsed.scheme.startswith('http') or not parsed.netloc:
                print("URL 형식이 잘못되었습니다.")
                continue # 재입력
            try:
                response = requests.head(self.base_url, timeout=5)
                # 정상이라면
                if response.status_code < 400: 
                    self.folder_name = "file_" + parsed.netloc.replace('.', '_').replace(':', '_')
                    print(f"저장 폴더명: {self.folder_name}")
                    break
                # 400이상의 상태 코드 발생 시 재입력
                else: 
                    print(f"서버 상태코드: {response.status_code}, 다시 입력하세요.")
            except Exception as e:
                print(f"접속 실패: {e}")

    def make_folder(self):
        '''폴더 생성'''
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        self.SAVE_DIR = os.path.join(BASE_DIR, self.folder_name)
        os.makedirs(self.SAVE_DIR, exist_ok=True) # 현재 실행 중인 파일 기준 디렉토리 생성

    def edit_filename(self, filename, max_length=50):
        '''긴 파일명 처리'''
        filename = filename.split('?')[0].split('&')[0]
        filename = re.sub(r'[^a-zA-Z0-9_.-]', '_', filename)
        if len(filename) > max_length:
            hash_value = hashlib.md5(filename.encode('utf-8')).hexdigest()[:10]
            filename = f"{hash_value}_{filename[-max_length:]}"
        return filename
    
    def selenium_download_js(self, js_url):
        '''403 파일 우회 다운로드'''
        print(f"[Selenium 우회 요청] {js_url}")
        try:
            self._setup_driver()
            self.driver.get(js_url)
            time.sleep(2)

            # HTML 파싱
            js_content = self.driver.page_source
            soup = BeautifulSoup(js_content, 'html.parser')
            only_text = soup.get_text()
            
            # 파일 저장
            filename = self.edit_filename(os.path.basename(js_url) or "unnamed.js")
            save_path = os.path.join(self.SAVE_DIR, filename)
            with open(save_path, 'w', encoding='utf-8') as f:
                f.write(only_text.strip())
            print(f"[Selenium 저장 완료] {filename}")

        except Exception as e:
            print(f"[Selenium 다운로드 실패] {js_url} → {e}")
        finally:
            if self.driver:
                self.driver.quit()

    # 바이너리 파일인지
    def is_binary(self, file_path):
        with open(file_path, 'rb') as f:
            chunk = f.read(1024)
        return b'\x00' in chunk

    def download_file(self):
        '''웹 페이지 소스 파일 다운로드'''
        self._setup_driver()
        
        try:
            print("웹페이지 접속 중...")
            self.driver.get(self.base_url)
            WebDriverWait(self.driver, 15).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            self.html = self.driver.page_source
            selenium_cookies = {cookie['name']: cookie['value'] for cookie in self.driver.get_cookies()} #쿠키
        except Exception as e:
            print(f"에러 발생: {e}")
            return
        finally:
            if self.driver:
                self.driver.quit()

        # HTML 파싱 
        self.soup = BeautifulSoup(self.html, 'html.parser')
        EXTENSIONS = ['.js', '.html']
        tags_attrs = [('script', 'src'), ('link', 'href'), ('a', 'href')]


        for tag, attr in tags_attrs:
            for element in self.soup.find_all(tag):
                file_url = element.get(attr)
                if not file_url:
                    continue

                full_url = urljoin(self.base_url, file_url)
                parsed = urlparse(full_url)
                path = parsed.path

                if any(path.endswith(ext) for ext in EXTENSIONS) or ('.' not in os.path.basename(path)):
                    try:
                        # 클라우드 플레어 우회용 헤더
                        headers = { 
                            "User-Agent": random.choice(USER_AGENTS), 
                            "Accept": "*/*",
                            "Accept-Encoding": "gzip, deflate, br",
                            "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
                            "Referer": self.base_url,
                            "Connection": "keep-alive",
                            "Cache-Control": "max-age=0",
                            "Upgrade-Insecure-Requests": "1",
                            "Sec-Fetch-Dest": "document",
                            "Sec-Fetch-Mode": "navigate",
                            "Sec-Fetch-Site": "same-origin",
                            "Sec-Fetch-User": "?1"
                        }
                        res = requests.get(full_url, headers=headers, cookies=selenium_cookies, timeout=7)
                        res.raise_for_status()
                        
                        # 기본 filename 초기화 (문자열이 없을 경우 index.html로 지정)
                        filename = os.path.basename(path) or 'index.html'
                        filename = self.edit_filename(filename) # 긴 파일명 수정

                        # 다운받지 않은 파일만 추가
                        if filename in self.downloaded: # 이미 다운 받은 파일은 건너뛰기
                            continue 
                        self.downloaded.add(filename)

                        # 파일 저장 -> encoding추가 ***
                        save_path = os.path.join(self.SAVE_DIR, filename)
                        
                        with open(save_path, 'wb') as f: 
                            f.write(res.content)
                        print(f"저장됨: {filename}")
                        
                    # 403 에러 파일은 재시도 
                    except RequestException as e:
                        print(f"다운로드 실패: {full_url} ({e})")
                        if "403" in str(e):
                            self.selenium_download_js(full_url) # 함수 호출
    
    
    # 압축 혹은 난독화된 js 파일 -> JavaScript 디코더나 Beautifier
    def decode_or_unzip(self,file_path):
        with open(file_path, "r") as f:
            f.read()
    
    
    def extract_js(self):
        '''JS 파일 추출'''
        for filename in os.listdir(self.SAVE_DIR):
            filepath = os.path.join(self.SAVE_DIR, filename)
            
            # js, html, 확장자 없는 파일들 중 
            if filename.endswith(('.js', '.html')) or '.' not in filename:
                is_html = filename.endswith('.html')
                try:
                    
                    if (self.is_binary(filepath)):
                        continue
                    if self.is_brotli_compressed(filepath):
                        continue
                    
                    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        
                        # html 태그가 있는 파일은 파싱해서 리스트에 추가
                        if not is_html and '<html' in content.lower():
                            is_html = True
                        if is_html:
                            soup = BeautifulSoup(content, 'html.parser')
                            scripts = soup.find_all('script')
                            script_content = "\n\n".join(script.string.strip() for script in scripts if script.string)
                            if script_content:
                                self.js_list.append((filename, script_content))
                        
                        # js는 바로 리스트에 추가
                        else:
                            self.js_list.append((filename, content))
                except Exception as e:
                    print(f"파일 분석 실패: {filename} ({e})")
        print(f"\n    최종 JS 파일 수: {len(self.js_list)}개")

    def remove_annotation(self, js_code):
        '''주석 삭제'''
        js_code = re.sub(r'/\*[\s\S]*?\*/', '', js_code) # /**/ 삭제
        js_code = re.sub(r'//.*', '', js_code) # //삭제
        return js_code

    def combine_js(self):
        '''JS코드 추합 파일 생성'''
        combined_code = []
        for filename, content in self.js_list:
            clean_code = self.remove_annotation(content) # 주석 삭제
            combined_code.append(f"\n\n// ===== {filename} =====\n{clean_code.strip()}") # 파일 이름 표시

        # 저장
        with open("combined.txt", 'w', encoding='utf-8') as f:
            f.writelines(combined_code)
        print(f"\n정리된 JS 코드 저장 완료: combined.txt")

def main():
    mfb = MakeFileByUrl()
    mfb.get_url()
    mfb.make_folder()
    mfb.download_file()
    mfb.extract_js()
    mfb.combine_js()
