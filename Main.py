from Clovax import main as clova_main
from Pattern import SignatureDetector
from UrlLoader import main as url_main
from Result import FinalResult

if __name__ == "__main__":
    # JS 추출하고 - 링크 입력받아서 진행
    url_main()
    
    # AI 난독화 복호화와 정적분석 - 파일 입력받아서 진행 (combined.txt)
    clova_main()
    
    # 시그니처 기반 정적 분석 - 파일 입력받아서 진행 (combined.txt)
    detector = SignatureDetector()
    detector.scan_file()
    cnt = detector.process_patterns() # 패턴 탐지 개수 파라미터로 넘겨주기
    detector.make_file()
    
    # 결과 - 파일 입력없이 즉시 출력
    result = FinalResult() # 객체 생성
    result.extract_from_clovax() # 유의미한 json만 추출해서 clovax_extraction.txt로 내보내기
    result.combine_results(cnt) # 추출된 결과를 하나의 final.txt로 내보내고 최종 결과 터미널 출력
    
    # 자동 종료 방지
    input("\n창을 닫으려면 엔터 키를 누르세요.")