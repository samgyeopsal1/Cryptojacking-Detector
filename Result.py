import re

class FinalResult:
    def __init__(self):
        pass

    def extract_from_clovax(self):
        '''유의미한 JSON만 추출하기'''
        
        self.extracted = []
        # 파일 입력받기
        while True:
            try:
                # file_path = input("검사할 파일을 입력하세요(clovax_analysis_result.txt): ")
                with open("clovax_analysis_result.txt", "r", encoding="utf-8") as f:
                    content = f.read()
                break
            except FileNotFoundError:
                print("파일이 존재하지 않습니다.")
            except Exception as e:
                print(f"[!] 파일 열기 실패: {e}")
            
        # [조각 n 결과] 기준으로 chunk를 나누고 split_chunks에 리스트로 저장
        split_chunks = re.split(r"(?=\[조각 \d+ 결과\])", content)

        # 제외할 형태 패턴 정의
        exclude_patterns = [
            r"\[조각 \d+ 결과\]\s*```json\s*\[\]\s*```",    # [조각 n 결과]'''json[]''' 제외
            r"\[조각 \d+ 결과\]\s*```json\s*\{\}\s*```",    # [조각 n 결과]'''json{}''' 제외
            
        ]

        # 조각으로 나뉜 리스트에 대해 chunk 검사
        for chunk in split_chunks:
            chunk = chunk.strip()
            
            # 1. 조각 문자열이 없으면 건너뛰고
            if not chunk:
                continue
            
            # 2. '''json{}'''과 같은 형태가 아니면 건너뛰고 ( [], {}, 에러발생 등 )
            json_match = re.search(r"```(?:json)?\s*(\{.*?\}|\[.*?\])\s*```", chunk, re.DOTALL)
            if not json_match:
                continue
            
            # 3. 제외 패턴에 해당하면 건너뛰고 ( '''json{}''' or '''json[]''' )
            if any(re.fullmatch(pattern, chunk, re.DOTALL) for pattern in exclude_patterns):
                continue  
            
            # 4. 백틱 제거 ( '''json{...}''' ->  {...} )
            match = re.search(r"```(?:json)?\s*(\{.*?\}|\[.*?\])\s*```", chunk, re.DOTALL)
            if not match:
                continue
            header = match.group(1)
            
            # 6. 키에 해당하는 값이 []면 건너뛰기  ( {crypto : []}처럼 딕셔너리 형태이지만 값이 없을 경우 )
            stripped_header = re.sub(r"\s+", "", header) 
            
            # 전체가 빈 딕셔너리면 건너뜀
            if stripped_header == "{}" or stripped_header == "[]":
                continue
            
            matches1 = re.findall(r'"\w+":\[\]', stripped_header) # ":[] 형태면 matches 리스트에 담기 
            matches2 = re.findall(r'"\w+":\{\}', stripped_header) # ":{} 형태면 matches 리스트에 담기
            if matches1 or matches2 : #and len(matches) == len(re.findall(r'"\w+":\[.*?\]', stripped_header)):  {crypto:[]},{crypto:[]} 이렇게 여러 쌍의 딕셔너리가 존재할 때
                continue
            
            # 유효한 JSON 문자열만 리스트에 추가
            self.extracted.append(header)
        
        # 파일로 저장
        output_path="clovax_extraction.txt"
        with open(output_path, "w", encoding="utf-8") as f:
            for chunk in self.extracted:
                f.write(chunk + "\n\n")
        print("clovax_extraction.txt 파일이 저장되었습니다.")

    def combine_results(self, cnt):
        '''최종 결과 저장 및 출력'''
        # final.txt 파일에 전체 탐지 내용 저장
        try:
            with open("final.txt", "w", encoding="utf-8") as f:
                for result1 in self.extracted: #clova
                    f.write(result1+"\n\n")
                f.write("\n")
                with open("signature_result.json", "r", encoding="utf-8") as file: #signautre
                    result2 = file.read()
                f.write(result2 + "\n\n")
            print("final.txt 파일이 저장되었습니다.")
        except Exception as e:
            print(f"[!] 파일 열기 실패 : {e}")

        # 결과 출력
        print("\n[최종 결과]")
        # 모든 탐지 방법에서 탐지될 경우 : 위험
        if len(self.extracted)>=1 and cnt>=1:
            print("🔴 [위험] cryptojacking 시도 중인 사이트입니다. 🔴")
            print(f"AI 정적분석에서 {len(self.extracted)}개, 시그니처 기반 정적분석에서 {cnt}개의 위험요소가 발견되었습니다.")
        # 한 가지 탐지 방법에서만 탐지될 경우 : 의심
        elif ( len(self.extracted)>=1 and cnt==0) or ( len(self.extracted)==0 and cnt>=1):
            print("🟡 [의심] cryptojacking 시도 중인 사이트일 가능성이 높습니다. 🟡")
            print(f"AI 정적분석에서 {len(self.extracted)}개, 시그니처 기반 정적분석에서 {cnt}개의 위험요소가 발견되었습니다.")
        # 모든 탐지 방법에서 탐지되지 않은 경우 : 안전
        elif len(self.extracted)==0 and cnt==0:
            print("🟢 [안전] 감지된 cryptojacking 요소가 없습니다. 🟢")
            print(f"AI 정적분석에서 {len(self.extracted)}개, 시그니처 기반 정적분석에서 {cnt}개의 위험요소가 발견되었습니다.")
