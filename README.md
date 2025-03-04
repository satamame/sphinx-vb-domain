# sphinx-vb-domain

## Overview

Sphinx extension to handle Visual Basic function directive, and also create the directives from document comments in VB source code.

This project is really experimental. Only features below are working but without any assurance.

## Installation

### pip

```
pip install sphinx-vb-domain
```

### rye

```
rye add --dev sphinx-vb-domain
```

## Usage

### conf.py

Add it to `extensions`.

```python
# conf.py

extensions = [
    'sphinx_vb_domain',
]
```

### Function directive

For example.

```restructuredtext
.. vb:function:: Private Function getId(ByVal name As String, ByVal age As Integer) As Integer
   :module: Module1

   A simple private function.

   :param name: Name
   :type name: String
   :param age: Age
   :type age: Integer
   :returns: Id
   :rtype: Integer

   Remarks here.
```

### Autodoc

To creade document from VB document comments, following config is needed.

```python
# conf.py

vb_autodoc_paths = [
    ('vb-src-dir', 'page-path', 'page-title'),
]
```

- `vb-src-dir`
    - Path to directory contains VB source, relative from conf.py (e.g. '../../macros').
- `page-path`
    - Path to reST file tobe created, relative from Sphinx source directory (e.g. 'modules' will create 'modules.rst').
- `page-title`
    - Title (level-1 headline) added to e.g. modules.rst.

Then, run sphinx-build with `-D vb_autodoc=1` parameter.

In file at `page-path` (e.g. 'modules.rst'), Module (level-2 headline) is created per vb file in `vb-src-dir`, and function directives under the Modules.

### Cross-references

When function directives are rendered, they come with a headline so that the directives appear in toctree.  
Also, the headline will be a cross-reference target.

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
> `module_name` and `function_name` are encoded if they contain characters invalid as target name.

## Known issues

- Function directive always rendered in Japanese like follows.
    ```
    Private Function getId(ByVal name As String, ByVal age As Integer) As Integer
    
        A simple private function.

        パラメータ: ・name (String) -- Name
                    ・age (Integer) -- Age
        戻り値: Id
        戻り値の型: Integer

        Remarks here.
    ```
    - You can change `doc_field_types` definition of `VBFunction` class.
