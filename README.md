# project2
>**크립토재킹(Cryptojacking)** 이란 ?
>
>크립토재킹은 사용자의 동의 없이 웹사이트나 악성 스크립트를 통해 CPU 자원을 몰래 사용해 가상화폐를 채굴하는 사이버 공격입니다.


>이 프로그램은 사용자가 입력한 URL을 분석하여, 해당 사이트에 크립토재킹(Cryptojacking) 을 수행하는 JavaScript가 포함되어 있는지를 탐지하고, 그 결과를 사용자에게 알려주는 기능을 제공합니다.                                  

>탐지 방식으로는 시그니처 탐지와 AI를 이용한 문맥 탐지를 진행합니다.                                  
>시그니처 탐지 : 도구 개발 시 개발자가 입력해둔 특정 키워드가 있는지를 탐색                                                
>AI 문맥 탐지 : 크립토재킹을 실행시키는 코드나 의심스러운 코드에 대해서 탐지함 (난독화 및 소형화 코드에 대해서도 탐지가 가능함) 
> <br/>


## 설치 방법
Git이 설치되어 있어야 합니다.
```bash
git clone https://github.com/samgyeopsal1/Cryptojacking-Detector.git
cd project2
pip install -r requirements.txt
python Main.py
```
<br/>

## 사용 방법
### 0. env 파일 첨부
- project2 폴더에 Clova API 키를 작성한 .env 파일을 저장합니다.                                              
![0단계 - 파일 첨부](screenshots/step0.png)


### 1. URL 입력
- Main.py를 실행합니다.
- 크립토재킹에 대해 탐지할 대상 URL을 입력합니다.
![aa](https://github.com/user-attachments/assets/39bb3d4c-866d-4a63-91b8-2b9d715787f5)


### 2. 대상 URL에 대해서 크롤링 시도
- Selenium을 이용해 대상 URL에서 로드되는 리소스에 대해서 모두 크롤링을 진행합니다.
- 크롤링한 리소스를 정제하여 combined.txt로 저장합니다.
![as](https://github.com/user-attachments/assets/5a511a17-c114-4c51-b736-b2131495bc48)


### 3. 크롤링한 리소스를 저장 후 탐지 진행
- combinet.txt 파일에 대해서 AI기반 문맥 탐지 및 시그니처 탐지를 진행합니다.
- 시그니처 탐지는 크립토재킹 의심 키워드와 combined.txt내에 있는 JavaScript와 비교하는 방식입니다.
- AI기반 문맥 탐지는 난독화 및 소형화 된 JavaScript도 전부 탐지할 수 있습니다. 탐지 방식은 핵심 키워드의 주변 구조를 분석하여, 코드가 난독화되거나 소형화되어도 고유한 패턴을 기반으로 크립토재킹을 탐지하는 방식입니다.


### 4. 사용자에게 각 탐지 방식의 결과 반환
- AI 탐지 및 시그니처 탐지 모두 탐지된 내용이 없을 시 '안전'
- AI 탐지 및 시그니처 탐지 둘 중 하나라도 탐지된 경우 '의심'
- AI 탐지 및 시그니처 탐지 모두 탐지된 경우 '위험'을 출력합니다.
![3단계 - 결과 출력](screenshots/s3.png)
