# sphinx-vb-domain

## 概要

Visual Basic の関数ディレクティブを処理する Sphinx 拡張機能です。VB のソースコード内のドキュメントコメントからそれらのディレクティブを作ることもできます。

これは実験的なプロジェクトです。以下に述べる機能がありますが、いつも正しく動くという保証はありません。

## インストール

### pip

```
pip install sphinx-vb-domain
```

### rye

```
rye add --dev sphinx-vb-domain
```

## 使い方

### conf.py

`extensions` に追加します。

```python
# conf.py

extensions = [
    'sphinx_vb_domain',
]
```

### 関数ディレクティブ

例

```restructuredtext
.. vb:function:: Private Function getId(ByVal name As String, ByVal age As Integer) As Integer
   :module: Module1

   これは単純な private 関数です。

   :param name: 名前
   :type name: String
   :param age: 年齢
   :type age: Integer
   :returns: Id
   :rtype: Integer

   ここに注意事項などを書きます。
```

### Autodoc

VB のドキュメントコメントからドキュメントを作成するには、以下の設定が必要です。

```python
# conf.py

vb_autodoc_paths = [
    ('vb-src-dir', 'page-path', 'page-title'),
]
```

- `vb-src-dir`
    - VBソースを含むディレクトリへの、conf.py からの相対パス (e.g. '../../macros')。
- `page-path`
    - 生成する reST ファイルの、source ディレクトリからの相対パス。'modules' と書くと 'modules.rst' が生成される。
- `page-title`
    - reST ファイルに追加されるタイトル (レベル1の見出し)。

設定を書いたら `-D vb_autodoc=1` という引数をつけて sphinx-build を実行します。

`page-path` で指定した reST ファイル (e.g. 'modules.rst') に、`vb-src-dir` ディレクトリ内の VB ファイルごとに「モジュール」(レベル2の見出し) が作られ、その下に関数ディレクティブが作られます。

### クロスリファレンス

関数ディレクティブには見出しが付くので、toctree に含まれるようになります。  
また、クロスリファレンスのターゲットとして使えます。

#### reStructuredText

```restructuredtext
* :vb:function:`module_name.function_name`
* :any:`module_name.function_name`
* :any:`Link text <module_name.function_name>`
```

#### MyST

```markdown
- {vb:function}`module_name.function_name`
- <project:#module_name.function_name>
- [Link text](#module_name.function_name)
```

> [!NOTE]
> `module_name` や `function_name` がターゲット名として使えない文字を含む場合、適当なターゲット名に変換 (エンコード) されます。

## 既知の問題

- 関数ディレクティブは、言語設定に関わらず以下のように日本語でレンダリングされます。
    ```
    Private Function getId(ByVal name As String, ByVal age As Integer) As Integer
    
        A simple private function.

        パラメータ: ・name (String) -- Name
                    ・age (Integer) -- Age
        戻り値: Id
        戻り値の型: Integer

        Remarks here.
    ```
    - これを変えたい場合は、`VBFunction` クラスの `doc_field_types` の内容を書き換えてください。
