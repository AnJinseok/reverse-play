# -*- coding: utf-8 -*-
"""
GAME EDITOR PNG 이미지를 Windows용 icon.ico로 변환하는 스크립트.

실행: python create_icon.py
필요: pip install Pillow
출력: icon.ico (프로젝트 루트) — GUI 창 및 exe 아이콘에 사용
"""

import os
import sys


def main() -> None:
    """img 폴더의 PNG를 읽어 icon.ico를 생성합니다."""
    try:
        from PIL import Image
    except ImportError:
        print('Pillow가 필요합니다: pip install Pillow')
        sys.exit(1)

    base = os.path.dirname(os.path.abspath(__file__))
    png_name = 'edit.png'
    png_path = os.path.join(base, 'img', png_name)
    ico_path = os.path.join(base, 'icon.ico')

    if not os.path.isfile(png_path):
        print(f'PNG를 찾을 수 없습니다: {png_path}')
        sys.exit(1)

    img = Image.open(png_path)
    # PNG에 투명 채널이 있으면 RGBA, 없으면 RGB로 통일
    if img.mode not in ('RGBA', 'RGB'):
        img = img.convert('RGBA')
    elif img.mode == 'RGB':
        img = img.convert('RGBA')

    # Windows ICO에 넣을 크기들
    sizes = [(16, 16), (32, 32), (48, 48), (256, 256)]
    img.save(ico_path, format='ICO', sizes=sizes)
    print(f'생성 완료: {ico_path}')


if __name__ == '__main__':
    main()
