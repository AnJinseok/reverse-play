# Big Ambitions 세이브 파일 수정 도구

`.hsg` 세이브는 **GZIP 압축 + 바이너리** 구조입니다. 이 스크립트로 Money, Energy, NetWorth 값을 수정할 수 있습니다.

**비공식 팬 도구**이며, Big Ambitions 개발사(Hovgaard Games)와 제휴·승인된 것이 아닙니다. 개인 사용·교육 목적으로만 사용하고, 게임 이용약관(EULA) 및 해당 국가 법률을 확인한 후 사용할 책임은 사용자에게 있습니다.

## 요구 사항

- **Python 3** (설치 필요)

## 사용법

### 0) 화면(GUI)으로 사용하기

```bash
python edit_save_gui.py
```

- **찾아보기**로 `.hsg` 세이브 파일 선택
- **현재 값**이 자동으로 표시됨 (다시 읽기 버튼으로 갱신 가능)
- **수정할 값**에 Money / Energy / NetWorth 입력 (비워두면 해당 항목은 변경 안 함)
- **저장 (덮어쓰기)** 또는 **다른 이름으로 저장**으로 적용
- 필요 시 "저장 시 원본을 .hsg.bak 으로 백업" 체크 유지

### 1) 현재 값만 보기 (수정 없음)

```bash
python edit_save.py "세이브경로\저장이름.hsg" --read-only
```

### 2) Money만 수정 (예: 100만으로)

```bash
python edit_save.py "세이브경로\저장이름.hsg" -m 1000000
```

- 원본은 자동으로 `저장이름.hsg.bak` 으로 백업됩니다.
- 같은 파일에 덮어쓰기 됩니다.

### 3) 여러 값 동시 수정

```bash
python edit_save.py "세이브경로\저장이름.hsg" -m 500000 -e 100 -n 1000000
```

- `-m` Money  
- `-e` Energy  
- `-n` NetWorth  

### 4) 다른 이름으로 저장 (원본 유지)

```bash
python edit_save.py "원본.hsg" -o "수정본.hsg" -m 999999
```

### 5) 백업 없이 덮어쓰기

```bash
python edit_save.py "세이브경로\저장이름.hsg" -m 1000000 --no-backup
```

## 실행 파일(.exe)로 만들기

Python 없이 단일 exe로 쓰고 싶다면:

```bash
pip install -r requirements-build.txt
python create_icon.py   # 아이콘 사용 시 한 번 실행 → icon.ico 생성
python build_exe.py
```

- 생성 위치: `dist\BigAmbitions_SaveEditor.exe`
- 이 exe만 복사해서 다른 PC에서도 실행 가능 (Windows 기준).
- `icon.ico`가 있으면 exe 파일 아이콘과 실행 창 아이콘에 적용됩니다.

### 빌드 시 "Permission denied" / "update_exe_pe_checksum failed" 나올 때

- **기존 exe를 종료**한 뒤 다시 빌드하세요. (실행 중인 exe는 수정할 수 없음)
- **탐색기에서 `dist` 폴더**를 열어 둔 상태면 닫고 다시 시도하세요.
- **백신·Windows Defender**가 exe를 검사하며 잠그는 경우: 20회 재시도 후 성공할 수도 있고, 실패하면 해당 폴더를 실시간 검사 예외에 추가한 뒤 다시 빌드하세요.

## 주의사항

- **게임을 끈 상태**에서 세이브 파일을 수정하세요.
- 게임 버전(EA 0.9 등)이 바뀌면 필드 위치가 달라져 수정이 실패할 수 있습니다.
- Energy/NetWorth는 게임 내 표시 방식(비율, 단위 등)에 따라 체감이 다를 수 있습니다.

## GitHub에 올리기

### A) reverse-play 레포 안에 디렉터리 하나로 넣기

[reverse-play](https://github.com/AnJinseok/reverse-play) 레포 안에 `big_ambitions_save_editor` 폴더로 넣어서, 나중에 다른 게임 에딧/공부용 프로젝트도 같은 레포에 디렉터리만 추가해서 올리고 싶을 때:

**1. reverse-play 루트 폴더 준비**

```bash
# 예: 상위 폴더로 가서 reverse-play 클론 (또는 이미 클론해 둔 폴더로 이동)
cd e:\1.workspace\4.python\1.game
git clone https://github.com/AnJinseok/reverse-play.git
cd reverse-play
```

**2. 이 프로젝트를 서브디렉터리로 복사**

- 지금 이 폴더(`big_ambitions_save_editor`) **전체**를 `reverse-play` 안에 그대로 복사해서  
  `reverse-play/big_ambitions_save_editor/` 가 되게 둡니다.  
  (탐색기에서 폴더 복사 후 붙여넣기, 또는 아래처럼 한 번에)

```bash
# reverse-play 폴더 안에서 실행 (현재 프로젝트 경로는 본인 환경에 맞게)
xcopy /E /I "e:\1.workspace\4.python\1.game\1.big_ambitions_save_editor" "big_ambitions_save_editor"
```

**3. 커밋 후 푸시**

```bash
git add big_ambitions_save_editor
git commit -m "초기 커밋: Big Ambitions 세이브 에디터 (GUI + CLI)"
git branch -M main
git push -u origin main
```

이후 레포 구조는 다음과 같습니다.

```
reverse-play/
  big_ambitions_save_editor/
    edit_save.py
    edit_save_gui.py
    README.md
    ...
  (나중에 다른 프로젝트 폴더 추가)
```

### B) 이 프로젝트만 단일 레포로 쓰기

1. GitHub에서 **새 저장소** 생성 (이름 예: `big-ambitions-save-editor`). README/라이선스 자동 생성은 하지 않아도 됨.
2. **지금 이 폴더**에서:

```bash
git init
git add .
git commit -m "초기 커밋: Big Ambitions 세이브 에디터 (GUI + CLI)"
git branch -M main
git remote add origin https://github.com/AnJinseok/<저장소명>.git
git push -u origin main
```

---

- `.gitignore`에 의해 `__pycache__/`, `build/`, `dist/`, `*.hsg`, `*.hsg.bak` 등은 커밋에서 제외됩니다.
- `icon.ico`는 `create_icon.py`로 생성하는 파일이므로, 올려도 되고 `.gitignore`에 넣어서 제외해도 됩니다. (이미지 원본은 `img/` 에 있음)

## 다른 값 수정이 필요할 때

- **Cheat Engine** 테이블을 쓰면 게임 실행 중에 돈, 에너지, 시간 등을 실시간으로 바꿀 수 있습니다.
- 공식 포럼: [Big Ambitions Community](https://forum.bigambitionsgame.com/)
