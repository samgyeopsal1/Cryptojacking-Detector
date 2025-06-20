# project2
>**크립토재킹(Cryptojacking)** 이란 ?
>
>크립토재킹(Cryptojacking)은 사용자의 동의 없이 웹사이트나 악성 스크립트를 통해 CPU 자원을 몰래 사용해 가상화폐를 채굴하는 사이버 공격입니다.


>이 프로그램은 사이트 내 **크립토재킹(Cryptojacking)** 을 실행시키는 JavaScript를 탐지하여 사용자에게 결과를 반환합니다.           
>탐지 방식으로는 시그니처 탐지(입력해둔 패턴과 대조하여 탐지)와 AI를 이용한 문맥 탐지를 진행합니다.
>시그니처 탐지 : 도구 개발 시 개발자가 입력해둔 특정 키워드가 있는지를 탐색
>AI 문맥 탐지 : 크립토재킹을 실행시키는 코드나 의심스러운 코드에 대해서 탐지함 (난독화 및 소형화 코드에 대해서도 탐지가 가능함) 
> <br/>


## 설치 방법
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
- 검사할 웹사이트의 URL을 입력하면,
- 해당 URL에서 JavaScript 파일만을 자동 추출하여 combined.txt 파일로 저장합니다.
![1단계 - URL 입력](screenshots/s1.png)

### 2. JavaScript 코드 분석
- Clova API를 이용해 의심 키워드를 분석합니다. 
![2단계 - 코드 분석](screenshots/s2.png)

### 3. 결과 출력
- 전체 탐지 결과를 final.txt 파일로 저장합니다.
- 사이트의 위험도를 안전/의심/위험으로 출력합니다.
![3단계 - 결과 출력](screenshots/s3.png)
