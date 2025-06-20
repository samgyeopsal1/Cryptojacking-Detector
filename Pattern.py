import re
import json

PATTERNS = [
    # 새로 추가된 키워드들
    r'deepminer', r'webminepool', r'monero', r'throttle', r'\.start\(\)', r'webminer',
    r'mining', r'moneroocean', r'walletAddress', r'workerId', r'threads',
    r'Anonymous', r'startMining', r'throttleMiner', r'forceASMJS',
    r'pool', r'worker', r'wss', r'crypto', r'root', r'cloudminer'
]

class SignatureDetector:
    def __init__(self):
        self.hits_count = []
        self.content = ""

    def scan_file(self):
        '''추출된 JS코드 스캔'''
        
        while True:
            try:
                filepath = "combined.txt"
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    self.content = f.read()
                break
            except Exception as e:
                print(f"[!] 파일 열기 실패: {filepath} ({e})")

    def process_patterns(self):
        '''패턴 탐지 결과 리스트에 저장'''
        
        for pattern in PATTERNS:
            matches = re.findall(pattern, self.content, re.IGNORECASE)
            if matches:
                hit_count = len(matches)
                self.hits_count.append((pattern, hit_count))
        return len(self.hits_count)

    def make_file(self):
        '''결과 파일 json으로 저장'''
        
        try:
            file_path = "signature_result.json"
            result_list = [
                {"signature": pattern, "count": hit_count}
                for pattern, hit_count in self.hits_count
            ]
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(result_list, f, ensure_ascii=False, indent=2)
            print(f"{file_path}파일이 저장되었습니다.")
        
        except Exception as e:
            print(f"[!] 파일 열기 실패 : {e}")
