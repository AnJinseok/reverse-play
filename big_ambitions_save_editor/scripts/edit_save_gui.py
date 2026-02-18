# -*- coding: utf-8 -*-
"""
Big Ambitions (.hsg) 세이브 파일 수정 - 화면(GUI) 버전

tkinter 기반 단일 화면에서 파일 선택, 현재 값 확인, Money/Energy/NetWorth 수정 및 저장을 수행합니다.
게임 기본 폴더(AppData\\LocalLow\\Hovgaard Games\\Big Ambitions)의 세이브 목록을 화면에 표시합니다.
"""

import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

# 기존 edit_save 모듈의 읽기/쓰기 함수 사용
from edit_save import (
    read_current_values,
    edit_save,
)


# .hsg 기본 필터
FILE_TYPES = [('Big Ambitions 세이브', '*.hsg'), ('모든 파일', '*.*')]

# Unity 기본 저장 위치 (Windows)
# Company: Hovgaard Games, Product: Big Ambitions
def get_default_game_root() -> str:
    """
    Big Ambitions 게임 루트 폴더 경로를 반환합니다.
    반환: ...\\AppData\\LocalLow\\Hovgaard Games\\Big Ambitions
    """
    user = os.environ.get('USERPROFILE', os.path.expanduser('~'))
    return os.path.join(user, 'AppData', 'LocalLow', 'Hovgaard Games', 'Big Ambitions')


def get_default_savegames_dir() -> str:
    """
    게임 세이브가 들어 있는 SaveGames 폴더 경로를 반환합니다.
    반환: ...\\Big Ambitions\\SaveGames
    """
    return os.path.join(get_default_game_root(), 'SaveGames')


def scan_hsg_files(top_dir: str) -> list[tuple[str, str]]:
    """
    지정 폴더 아래에서 재귀적으로 .hsg 파일을 찾아 (전체경로, 표시이름) 목록을 반환합니다.
    표시이름은 게임 폴더 기준 상대 경로입니다.
    입력: top_dir — 검색 루트 (예: SaveGames 경로)
    반환: [(full_path, display_name), ...]
    """
    root = os.path.normpath(top_dir)
    if not os.path.isdir(root):
        return []
    result = []
    for dirpath, _dirnames, filenames in os.walk(root):
        for name in filenames:
            if name.lower().endswith('.hsg'):
                full = os.path.join(dirpath, name)
                try:
                    rel = os.path.relpath(full, root)
                except ValueError:
                    rel = name
                result.append((full, rel))
    # 표시 이름 기준 정렬 (같은 폴더끼리 묶이도록)
    result.sort(key=lambda x: (x[1].lower(), x[0]))
    return result


def _icon_path() -> str | None:
    """
    아이콘 파일(icon.ico)의 전체 경로를 반환합니다.
    exe로 빌드된 경우 번들 내 경로, 스크립트 실행 시에는 프로젝트 루트 기준.
    반환: 경로 문자열. 없으면 None
    """
    if getattr(sys, 'frozen', False):
        base = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(base, 'icon.ico')
    return path if os.path.isfile(path) else None


def run_gui() -> None:
    """GUI 메인 창을 띄우고 이벤트 루프를 실행합니다."""
    root = tk.Tk()
    # 에디터 아이콘 설정 (icon.ico가 있으면)
    icon_path = _icon_path()
    if icon_path:
        try:
            root.iconbitmap(icon_path)
        except Exception:
            pass
    app = SaveEditorScreen(root)
    root.mainloop()


class SaveEditorScreen:
    """
    세이브 에디터 단일 화면.
    - 입력: 부모 Tk 창
    - 동작: 파일 선택, 현재 값 로드, 값 수정, 저장(덮어쓰기/다른 이름으로)
    """

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title('Big Ambitions 세이브 에디터')
        self.root.minsize(420, 380)
        self.root.resizable(True, True)

        # 현재 열린 파일 경로 (없으면 None)
        self._current_path: str | None = None

        self._build_ui()

    def _build_ui(self) -> None:
        """화면 위젯을 구성합니다."""
        main = ttk.Frame(self.root, padding=12)
        main.pack(fill=tk.BOTH, expand=True)

        # ---- 파일 선택 영역 ----
        file_frame = ttk.LabelFrame(main, text='세이브 파일', padding=6)
        file_frame.pack(fill=tk.X, pady=(0, 8))

        self._path_var = tk.StringVar()
        path_entry = ttk.Entry(file_frame, textvariable=self._path_var)
        path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6))

        def on_browse() -> None:
            initial = get_default_savegames_dir()
            if not os.path.isdir(initial):
                initial = get_default_game_root()
            path = filedialog.askopenfilename(
                title='세이브 파일 선택',
                filetypes=FILE_TYPES,
                initialdir=initial if os.path.isdir(initial) else None,
            )
            if path:
                self._path_var.set(path)
                self._on_file_selected(path)

        ttk.Button(file_frame, text='찾아보기', command=on_browse).pack(side=tk.RIGHT)

        # ---- 게임 세이브 폴더 (화면에 목록 표시) ----
        game_dir_frame = ttk.LabelFrame(main, text='게임 세이브 폴더', padding=6)
        game_dir_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 8))

        game_root = get_default_game_root()
        savegames_dir = get_default_savegames_dir()
        self._game_dir_var = tk.StringVar(
            value=savegames_dir if os.path.isdir(savegames_dir) else game_root
        )
        ttk.Label(game_dir_frame, textvariable=self._game_dir_var, foreground='gray').pack(
            anchor=tk.W
        )

        # .hsg 목록 리스트박스 + 스크롤
        list_container = ttk.Frame(game_dir_frame)
        list_container.pack(fill=tk.BOTH, expand=True, pady=(4, 0))
        scroll = ttk.Scrollbar(list_container)
        self._save_listbox = tk.Listbox(
            list_container,
            height=6,
            selectmode=tk.SINGLE,
            yscrollcommand=scroll.set,
            font=('Segoe UI', 9),
        )
        scroll.config(command=self._save_listbox.yview)
        self._save_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        # 클릭 시 선택한 파일 경로로 로드
        self._save_list_paths: list[str] = []

        def on_list_select(_event) -> None:
            sel = self._save_listbox.curselection()
            if sel and 0 <= sel[0] < len(self._save_list_paths):
                path = self._save_list_paths[sel[0]]
                self._path_var.set(path)
                self._on_file_selected(path)

        self._save_listbox.bind('<<ListboxSelect>>', on_list_select)
        self._save_listbox.bind('<Double-1>', on_list_select)

        btn_row = ttk.Frame(game_dir_frame)
        btn_row.pack(fill=tk.X, pady=(4, 0))
        ttk.Button(btn_row, text='목록 새로고침', command=self._refresh_save_list).pack(
            side=tk.LEFT, padx=(0, 6)
        )
        ttk.Button(btn_row, text='이 파일 열기', command=self._open_selected_from_list).pack(
            side=tk.LEFT
        )

        # 초기 목록 채우기
        self._refresh_save_list()

        # ---- 현재 값 표시 영역 ----
        current_frame = ttk.LabelFrame(main, text='현재 값 (읽기 전용)', padding=6)
        current_frame.pack(fill=tk.X, pady=(0, 8))

        self._current_labels = {}
        for name in ('Money', 'Energy', 'NetWorth'):
            row = ttk.Frame(current_frame)
            row.pack(fill=tk.X)
            ttk.Label(row, text=f'{name}:', width=10, anchor=tk.W).pack(side=tk.LEFT)
            lbl = ttk.Label(row, text='—', anchor=tk.W)
            lbl.pack(side=tk.LEFT, fill=tk.X, expand=True)
            self._current_labels[name] = lbl

        # ---- 수정 입력 영역 ----
        edit_frame = ttk.LabelFrame(main, text='수정할 값 (비워두면 변경 안 함)', padding=6)
        edit_frame.pack(fill=tk.X, pady=(0, 8))

        self._edit_vars = {}
        for name in ('Money', 'Energy', 'NetWorth'):
            row = ttk.Frame(edit_frame)
            row.pack(fill=tk.X)
            ttk.Label(row, text=f'{name}:', width=10, anchor=tk.W).pack(side=tk.LEFT)
            var = tk.StringVar()
            ent = ttk.Entry(row, textvariable=var, width=20)
            ent.pack(side=tk.LEFT, padx=(0, 8))
            self._edit_vars[name] = var

        # ---- 옵션 ----
        opt_frame = ttk.Frame(main)
        opt_frame.pack(fill=tk.X, pady=(0, 8))
        self._backup_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            opt_frame,
            text='저장 시 원본을 .hsg.bak 으로 백업',
            variable=self._backup_var,
        ).pack(anchor=tk.W)

        # ---- 버튼 영역 ----
        btn_frame = ttk.Frame(main)
        btn_frame.pack(fill=tk.X, pady=(0, 8))

        ttk.Button(btn_frame, text='현재 값 다시 읽기', command=self._reload_current).pack(
            side=tk.LEFT, padx=(0, 6)
        )
        ttk.Button(btn_frame, text='저장 (덮어쓰기)', command=self._save_overwrite).pack(
            side=tk.LEFT, padx=(0, 6)
        )
        ttk.Button(btn_frame, text='다른 이름으로 저장', command=self._save_as).pack(
            side=tk.LEFT
        )

        # ---- 상태 메시지 ----
        self._status_var = tk.StringVar(value='파일을 선택하거나 경로를 입력한 뒤 값을 확인·수정하세요.')
        ttk.Label(main, textvariable=self._status_var, foreground='gray').pack(
            anchor=tk.W
        )

    def _on_file_selected(self, path: str) -> None:
        """
        파일이 선택되었을 때 현재 값을 로드하여 화면에 반영합니다.
        입력: path — .hsg 파일 경로
        """
        self._current_path = path
        self._reload_current()

    def _refresh_save_list(self) -> None:
        """게임 세이브 폴더를 스캔하여 리스트박스에 .hsg 목록을 표시합니다."""
        self._save_list_paths.clear()
        self._save_listbox.delete(0, tk.END)
        search_dir = self._game_dir_var.get().strip() or get_default_savegames_dir()
        if not os.path.isdir(search_dir):
            search_dir = get_default_game_root()
        if not os.path.isdir(search_dir):
            self._save_listbox.insert(tk.END, '(게임 폴더를 찾을 수 없습니다)')
            return
        self._game_dir_var.set(search_dir)
        pairs = scan_hsg_files(search_dir)
        for _full, display in pairs:
            self._save_list_paths.append(_full)
            self._save_listbox.insert(tk.END, display)
        if not pairs:
            self._save_listbox.insert(tk.END, '(이 폴더에 .hsg 파일이 없습니다)')

    def _open_selected_from_list(self) -> None:
        """리스트박스에서 선택한 항목을 세이브 경로로 설정하고 로드합니다."""
        sel = self._save_listbox.curselection()
        if not sel or sel[0] >= len(self._save_list_paths):
            self._status_var.set('목록에서 세이브 파일을 선택하세요.')
            return
        path = self._save_list_paths[sel[0]]
        self._path_var.set(path)
        self._on_file_selected(path)

    def _reload_current(self) -> None:
        """경로가 있으면 해당 세이브의 현재 값을 읽어 라벨에 표시합니다."""
        path = self._path_var.get().strip()
        if not path:
            self._status_var.set('먼저 세이브 파일을 선택하세요.')
            return
        if not os.path.isfile(path):
            self._status_var.set(f'파일을 찾을 수 없습니다: {path}')
            return

        try:
            values = read_current_values(path)
            for name, lbl in self._current_labels.items():
                val = values.get(name, '—')
                if isinstance(val, (int, float)):
                    lbl.config(text=str(val))
                else:
                    lbl.config(text=str(val))
            self._status_var.set('현재 값을 불러왔습니다.')
        except Exception as e:
            self._status_var.set(f'읽기 오류: {e}')
            for lbl in self._current_labels.values():
                lbl.config(text='—')

    def _get_edit_numbers(self) -> dict[str, float | None]:
        """
        수정 입력란에서 숫자만 추출합니다. 빈 칸은 None.
        반환: 필드명 -> float 또는 None
        """
        result = {}
        for name, var in self._edit_vars.items():
            s = var.get().strip()
            if not s:
                result[name] = None
                continue
            try:
                result[name] = float(s)
            except ValueError:
                result[name] = None
        return result

    def _save_overwrite(self) -> None:
        """현재 경로에 덮어쓰기로 저장합니다."""
        path = self._path_var.get().strip()
        if not path or not os.path.isfile(path):
            messagebox.showwarning('저장 불가', '유효한 세이브 파일을 먼저 선택하세요.')
            return
        self._do_save(input_path=path, output_path=path)

    def _save_as(self) -> None:
        """다른 이름/경로로 저장합니다."""
        path = self._path_var.get().strip()
        if not path:
            messagebox.showwarning('저장 불가', '먼저 세이브 파일을 선택하세요.')
            return
        out = filedialog.asksaveasfilename(
            title='다른 이름으로 저장',
            defaultextension='.hsg',
            filetypes=FILE_TYPES,
            initialfile=os.path.basename(path),
        )
        if not out:
            return
        # 원본이 없어도 "다른 이름으로 저장"은 허용(현재는 읽기만 하므로 원본 필요)
        if not os.path.isfile(path):
            messagebox.showerror('오류', '원본 파일을 찾을 수 없습니다.')
            return
        self._do_save(input_path=path, output_path=out)

    def _do_save(
        self,
        input_path: str,
        output_path: str,
    ) -> None:
        """
        edit_save를 호출하여 수정 후 저장합니다.
        입력: input_path — 원본 .hsg, output_path — 저장할 경로
        """
        edits = self._get_edit_numbers()
        money = edits.get('Money')
        energy = edits.get('Energy')
        net_worth = edits.get('NetWorth')

        if money is None and energy is None and net_worth is None:
            messagebox.showinfo(
                '저장 안 함',
                '수정할 값이 없습니다. Money / Energy / NetWorth 중 하나 이상 입력하세요.',
            )
            return

        try:
            changes = edit_save(
                input_path,
                output_path,
                money=money,
                energy=energy,
                net_worth=net_worth,
                backup=self._backup_var.get(),
            )
            lines = ['저장 완료: ' + output_path]
            for name, (old, new) in changes.items():
                if isinstance(new, str):
                    lines.append(f'  {name}: {new}')
                else:
                    lines.append(f'  {name}: {old} -> {new}')
            self._status_var.set('저장했습니다.')
            messagebox.showinfo('저장 완료', '\n'.join(lines))
            # 저장 후 현재 값 다시 읽기
            self._current_path = output_path
            self._path_var.set(output_path)
            self._reload_current()
        except Exception as e:
            messagebox.showerror('저장 오류', str(e))
            self._status_var.set(f'저장 오류: {e}')


if __name__ == '__main__':
    run_gui()
