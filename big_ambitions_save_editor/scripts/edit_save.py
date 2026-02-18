# -*- coding: utf-8 -*-
"""
Big Ambitions (.hsg) 세이브 파일 수정 스크립트

.hsg 파일은 GZIP 압축된 바이너리이며, 내부에 UTF-16 필드명과 float 값이 저장됨.
Money, Energy, NetWorth 등 특정 필드의 값을 변경한 뒤 다시 압축하여 저장합니다.
"""

import gzip
import struct
import shutil
import argparse
import os


# 필드명(UTF-16)과 그 뒤에 오는 값 타입/오프셋 정보
# (실제 세이브에서 확인한 구조: 필드명 직후 4바이트 float)
FIELD_MONEY = b'M\x00o\x00n\x00e\x00y\x00'
FIELD_ENERGY = b'E\x00n\x00e\x00r\x00g\x00y\x00'
FIELD_NET_WORTH = b'N\x00e\x00t\x00W\x00o\x00r\x00t\x00h\x00'
# Energy는 필드명 뒤 구조가 다를 수 있음 (추가 타입 바이트 등)
VALUE_OFFSET_AFTER_FIELD = 0  # 필드명 끝(마지막 문자 2바이트) 바로 다음이 값인 경우


def find_field_value_offset(data: bytes, field_utf16: bytes, value_size: int = 4) -> int:
    """
    바이너리 데이터에서 UTF-16 필드명 위치를 찾고, 그 뒤 값의 시작 오프셋을 반환합니다.

    Args:
        data: 압축 해제된 세이브 바이너리
        field_utf16: UTF-16으로 인코딩된 필드명 (예: b'M\\x00o\\x00n\\x00e\\x00y\\x00')
        value_size: 값 크기(바이트). float=4, double=8

    Returns:
        값이 시작하는 바이트 오프셋. 없으면 -1
    """
    idx = data.find(field_utf16)
    if idx < 0:
        return -1
    # 필드명 길이만큼 건너뛴 뒤가 값 (일부 필드는 중간에 타입 바이트가 있을 수 있음)
    value_start = idx + len(field_utf16)
    if value_start + value_size > len(data):
        return -1
    return value_start


def read_float_at(data: bytes, offset: int) -> float:
    """지정 오프셋에서 little-endian float 4바이트를 읽습니다."""
    return struct.unpack('<f', data[offset : offset + 4])[0]


def write_float_at(data: bytearray, offset: int, value: float) -> None:
    """지정 오프셋에 little-endian float 4바이트를 씁니다."""
    data[offset : offset + 4] = struct.pack('<f', value)


def decompress_save(path: str) -> bytes:
    """
    .hsg 파일을 GZIP 해제하여 바이트 데이터를 반환합니다.

    Args:
        path: .hsg 파일 경로

    Returns:
        압축 해제된 바이너리
    """
    with gzip.open(path, 'rb') as f:
        return f.read()


def compress_and_save(data: bytes, path: str) -> None:
    """
    바이트 데이터를 GZIP으로 압축하여 .hsg 파일로 저장합니다.

    Args:
        data: 압축할 바이너리
        path: 저장할 .hsg 파일 경로
    """
    with gzip.open(path, 'wb') as f:
        f.write(data)


def edit_save(
    input_path: str,
    output_path: str,
    money: float = None,
    energy: float = None,
    net_worth: float = None,
    backup: bool = True,
) -> dict:
    """
    세이브 파일을 읽어 지정한 값만 수정한 뒤 저장합니다.

    Args:
        input_path: 원본 .hsg 파일 경로
        output_path: 수정된 파일을 저장할 경로 (같은 경로면 덮어쓰기)
        money: 설정 시 Money 값을 이 값으로 변경
        energy: 설정 시 Energy 값을 이 값으로 변경
        net_worth: 설정 시 NetWorth 값을 이 값으로 변경
        backup: True면 원본을 .hsg.bak으로 백업

    Returns:
        변경된 필드와 이전/이후 값을 담은 dict
    """
    # 압축 해제
    raw = decompress_save(input_path)
    data = bytearray(raw)
    changes = {}

    # Money 수정
    if money is not None:
        off = find_field_value_offset(data, FIELD_MONEY, 4)
        if off >= 0:
            old = read_float_at(data, off)
            write_float_at(data, off, money)
            changes['Money'] = (old, money)
        else:
            changes['Money'] = (None, '필드 찾기 실패')

    # Energy 수정 (구조가 동일하다고 가정)
    if energy is not None:
        off = find_field_value_offset(data, FIELD_ENERGY, 4)
        if off >= 0:
            old = read_float_at(data, off)
            write_float_at(data, off, energy)
            changes['Energy'] = (old, energy)
        else:
            changes['Energy'] = (None, '필드 찾기 실패')

    # NetWorth 수정
    if net_worth is not None:
        off = find_field_value_offset(data, FIELD_NET_WORTH, 4)
        if off >= 0:
            old = read_float_at(data, off)
            write_float_at(data, off, net_worth)
            changes['NetWorth'] = (old, net_worth)
        else:
            changes['NetWorth'] = (None, '필드 찾기 실패')

    # 백업
    if backup and os.path.abspath(input_path) == os.path.abspath(output_path):
        bak_path = input_path + '.bak'
        shutil.copy2(input_path, bak_path)

    # 압축하여 저장
    compress_and_save(bytes(data), output_path)
    return changes


def read_current_values(path: str) -> dict:
    """
    수정 없이 현재 세이브의 Money/Energy/NetWorth 값을 읽어 반환합니다.

    Args:
        path: .hsg 파일 경로

    Returns:
        필드명 -> float 값 또는 오류 메시지
    """
    raw = decompress_save(path)
    result = {}
    for name, field in [
        ('Money', FIELD_MONEY),
        ('Energy', FIELD_ENERGY),
        ('NetWorth', FIELD_NET_WORTH),
    ]:
        off = find_field_value_offset(raw, field, 4)
        if off >= 0:
            result[name] = read_float_at(raw, off)
        else:
            result[name] = '(필드 없음)'
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description='Big Ambitions .hsg 세이브 파일 수정')
    parser.add_argument('save_file', help='.hsg 세이브 파일 경로')
    parser.add_argument('-o', '--output', default=None, help='출력 파일 경로 (기본: 입력 파일 덮어쓰기)')
    parser.add_argument('-m', '--money', type=float, default=None, help='Money 값 설정')
    parser.add_argument('-e', '--energy', type=float, default=None, help='Energy 값 설정 (0~1 등)')
    parser.add_argument('-n', '--networth', type=float, default=None, help='NetWorth 값 설정')
    parser.add_argument('--no-backup', action='store_true', help='덮어쓸 때 백업 파일 생성 안 함')
    parser.add_argument('--read-only', action='store_true', help='수정 없이 현재 값만 출력')
    args = parser.parse_args()

    if not os.path.isfile(args.save_file):
        print('오류: 세이브 파일을 찾을 수 없습니다.', args.save_file)
        return

    # 읽기 전용: 현재 값만 출력
    if args.read_only:
        vals = read_current_values(args.save_file)
        print('현재 세이브 값:', vals)
        return

    output = args.output or args.save_file
    changes = edit_save(
        args.save_file,
        output,
        money=args.money,
        energy=args.energy,
        net_worth=args.networth,
        backup=not args.no_backup,
    )

    if changes:
        print('변경 사항:')
        for name, (old, new) in changes.items():
            if isinstance(new, str):
                print(f'  {name}: {new}')
            else:
                print(f'  {name}: {old} -> {new}')
        print('저장 완료:', output)
    else:
        print('변경할 항목이 없습니다. -m, -e, -n 중 하나 이상 지정하세요.')


if __name__ == '__main__':
    main()
