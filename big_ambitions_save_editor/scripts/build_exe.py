# -*- coding: utf-8 -*-
"""
GUI 프로그램을 단일 실행 파일(.exe)로 빌드하는 스크립트.

실행: python build_exe.py
필요: pip install pyinstaller (아이콘 사용 시 먼저 python create_icon.py 로 icon.ico 생성)
출력: dist/BigAmbitions_SaveEditor.exe (Windows)
"""

import os
import subprocess
import sys


def main() -> None:
    """PyInstaller를 호출하여 edit_save_gui.py 기준으로 onefile exe를 생성합니다."""
    base = os.path.dirname(os.path.abspath(__file__))
    # 어디서 실행하든 scripts 폴더 기준으로 동작하도록 작업 디렉터리 변경
    os.chdir(base)
    exe_path = os.path.join(base, 'dist', 'BigAmbitions_SaveEditor.exe')
    if os.path.isfile(exe_path):
        print('안내: 기존 exe가 있습니다. 빌드 중 "Permission denied" 가 나오면')
        print('  - BigAmbitions_SaveEditor.exe 실행 중이면 종료하고')
        print('  - dist 폴더 창을 닫은 뒤 다시 python build_exe.py 를 실행하세요.')
        print()
    cmd = [
        sys.executable,
        '-m',
        'PyInstaller',
        '--onefile',
        '--windowed',
        '--name',
        'BigAmbitions_SaveEditor',
        '--clean',
        'edit_save_gui.py',
    ]
    # icon.ico가 있으면 exe 아이콘 및 창 아이콘으로 사용
    icon_path = os.path.join(base, 'icon.ico')
    if os.path.isfile(icon_path):
        cmd.extend(['--icon', icon_path])
        # exe 실행 시 창 아이콘을 위해 번들에 포함
        cmd.extend(['--add-data', f'{icon_path}{os.pathsep}.'])
    else:
        print('참고: icon.ico가 없습니다. python create_icon.py 로 생성하면 exe/창 아이콘이 적용됩니다.')
    result = subprocess.run(cmd)
    if result.returncode != 0:
        sys.exit(result.returncode)
    print('빌드 완료. 실행 파일: dist\\BigAmbitions_SaveEditor.exe')


if __name__ == '__main__':
    main()
