# clovax_fullscan_oop.py
# 최종 - 이중 분석 모드 + 자동 재시도(backoff) 적용 + 분석 1회 성공 시 조기 종료

from openai import OpenAI
import time
import os
import sys
from dotenv import load_dotenv

# 안전하게 stdout, stderr reconfigure
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

class ClovaXScanner:
    def __init__(self, api_key, base_url="https://clovastudio.stream.ntruss.com/v1/openai/"):
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.max_len = 2500
        self.final_result = []

    def load_file(self):
        
        while True:
            try:
                filepath = "combined.txt"
                with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                    self.full_code = f.read()
                break
            except Exception as e:
                print(f"[!]파일 열기 실패 : {e}")
        
        print(f"읽은 파일 크기: {len(self.full_code)} bytes")
        self.chunks = [self.full_code[i:i+self.max_len] for i in range(0, len(self.full_code), self.max_len)]
        print(f"총 {len(self.chunks)}개의 조각으로 분할 완료\n")

    def analyze_chunks(self):
        SYSTEM_PROMPT = (
            
            #"당신은 사이버 보안 전문가입니다. 주어진 JavaScript 안에서 \n"
            #"- 남도화된 부분이 있으면 사람이 이해할 수 있도록 복원한 뒤, \n"
            #"- 복원된 코드 안에서 **크립토잭핑과 관련된 요소( 개인 유저 조회, Coinhive, WebAssembly miner, Web Worker 차단 )** 만을 탐지해 주세요.\n"
            #"결과는 다음과 같이 출력해 주세요:\n"
            #"1. 탐지된 항목만 JSON 형식으로 출력 (필요한 경우 파일명과 코드 조각 포함)\n"
            #"2. 불필요한 설명, 해설 문장은 쓰지 마세요.\n"
            #"3. 탐지된 항목이 없으면 비어 있는 JSON `{}` 만 출력해 주세요.\n"
            #"바로 JSON 형식만 출력해야 합니다."
              "당신은 사이버 보안 전문가입니다. 다음 JavaScript 코드를 분석해 주세요.\n\n"
                "1. 코드에 난독화가 있다면 사람이 이해할 수 있도록 복원한 후 분석합니다.\n"
                "2. 아래와 같은 특징이 하나라도 존재할 경우, 크립토재킹(cryptojacking)으로 간주합니다:\n"
                "   - Web Worker를 이용한 반복 연산 또는 무한 루프 수행\n"
                "   - WebAssembly(wasm)를 통해 연산을 분산 수행하거나 배포받는 구조\n"
                "   - setInterval 또는 requestAnimationFrame 등을 이용한 주기적 고부하 연산\n"
                "   - 외부 채굴 서버 또는 프록시 서버와 통신하며 job, submit, auth 등의 명령을 주고받음\n"
                "   - CPU를 장시간 점유하거나 background에서 실행되며 브라우저 리소스를 과도하게 사용하는 구조\n"
                "   - atob, eval, Function 등 난독화 후 실행하는 패턴을 통해 위 조건이 숨겨져 있는 경우\n\n"    
                "3. 아래 출력 형식에 맞춰 반드시 JSON 형식으로만 출력하세요:\n"
                "   - 탐지된 항목이 있다면 다음과 같이 출력:\n"
                "     { \"filename\": \"xxx.js\", \"reason\": \"WebAssembly miner detected\", \"code\": \"...의심 코드 일부...\" }\n"
                "   - 탐지된 항목이 없다면 반드시 빈 JSON `{}` 만 출력하세요.\n"
                "   - 해설, 설명, 분석 과정 등은 절대 포함하지 마세요. 결과만 출력하세요."
)        

        for idx, chunk in enumerate(self.chunks, 1):
            print(f"[{idx}/{len(self.chunks)}] 조각 이중 분석 중...")
            meaningful_result = None

            for trial in range(2):
                retries = 0
                while retries < 5:
                    try:
                        response = self.client.chat.completions.create(
                            model="HCX-005",
                            messages=[
                                {"role": "system", "content": SYSTEM_PROMPT},
                                {"role": "user", "content": chunk}
                            ]
                        )
                        result = response.choices[0].message.content.strip()
                        print(f"    [시도 {trial+1}] 분석 완료")

                        if result not in ("{}", "", "에러 발생"):
                            meaningful_result = result
                        break  # try-success

                    except Exception as e:
                        print(f"    [시도 {trial+1}] 분석 실패 (재시도 {retries+1}): {e}")
                        if "429" in str(e) or "rate" in str(e).lower():
                            wait = 2 ** retries
                            print(f"      → 요청 제한 감지: {wait}초 대기 후 재시도")
                            time.sleep(wait)
                            retries += 1
                        else:
                            meaningful_result = f"에러 발생: {e}"
                            break

                time.sleep(1)

                if meaningful_result:
                    break  # trial loop break if one success

            self.final_result.append(meaningful_result or "{}")

    def save_results(self, output_path="clovax_analysis_result.txt"):
        with open(output_path, "w", encoding="utf-8") as f:
            for idx, res in enumerate(self.final_result, 1):
                f.write(f"\n[조각 {idx} 결과]\n{res}\n")
        print("\n============================================================")
        # print(f"\nAI 정적 분석 결과 저장 완료: {output_path}")
        print(f"{output_path} 파일이 저장되었습니다.")
    def show_results(self):
        print("\n   전체 분석 결과:")
        for idx, res in enumerate(self.final_result, 1):
            print(f"\n[조각 {idx} 결과]")
            print(res)

def main():
    load_dotenv()
    time.sleep(2)
    api_key = os.getenv("KEY")  # 네 API 키
    scanner = ClovaXScanner(api_key)
    scanner.load_file()
    scanner.analyze_chunks()
    scanner.save_results()
