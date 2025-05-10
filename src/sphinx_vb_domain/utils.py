import hashlib
import re
from docutils.nodes import make_id


def to_safe_label(name: str, encode_: bool) -> str:
    '''Generate a valid label by encoding invalid characters with md5.'''
    invalid_symbols = re.compile(r'[!-/:-@\[-`{-~]')
    target_ptn = re.compile(r'[a-zA-Z0-9_\-]+')

    # Split name into parts.
    # e.g. 'Module1.Function1' -> ['Module1', 'Function1']
    name_parts = name.split('.')

    target_parts = []
    for name_part in name_parts:
        # ラベルに使えない記号をハイフンに置き換える。
        name_part = invalid_symbols.sub('-', name_part)

        # エンコードしない、またはする必要がない場合
        if not encode_ or target_ptn.fullmatch(name_part):
            target_part = name_part
        else:
            # ハッシュダイジェストを生成
            digest = hashlib.md5(
                name_part.encode('utf-8')).hexdigest()[:8]
            # 先頭が数字の場合に接頭辞を付ける
            target_part = f"x{digest}" if digest[0].isdigit() else digest

        target_parts.append(make_id(target_part))

    return '.'.join(target_parts)
