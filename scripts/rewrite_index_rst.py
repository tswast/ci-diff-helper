# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Rewrite the index.rst file generated by sphinx-apidoc.

This file is expected to be the file generated for the base
module ``ci_diff_helper/__init__.py``.
"""

import os
import types

try:
    import ci_diff_helper
except ImportError:
    ci_diff_helper = None


_BASE_PACKAGE = 'ci_diff_helper'
_EXPECTED_AUTOMODULE_LINES = (
    '',
    '.. automodule:: ci_diff_helper',
    '    :members:',
    '    :inherited-members:',
    '    :undoc-members:',
    '    :show-inheritance:',
    '',
)
_CURR_DIR = os.path.dirname(__file__)
DOCS_DIR = os.path.abspath(os.path.join(_CURR_DIR, '..', 'docs'))
INDEX_FILE = os.path.join(DOCS_DIR, 'index.rst')


def public_members():
    """Get public members in :mod:`ci_diff_helper` package.

    Returns:
        list: List of all public members **defined** in the
        main package.
    """
    if ci_diff_helper is None:
        return []

    members = []
    for name in dir(ci_diff_helper):
        # Filter out non-public.
        if name.startswith('_'):
            continue
        value = getattr(ci_diff_helper, name)
        # Filter out imported modules.
        if isinstance(value, types.ModuleType):
            continue
        # Only keep values defined in the base package.
        home = getattr(value, '__module__', _BASE_PACKAGE)
        if home == _BASE_PACKAGE:
            members.append(name)

    return members


def main():
    """Rewrite the index.rst file.

    Raises:
        ValueError: If the title '==...==' isn't on line 1.
        ValueError: If the title isn't the expected value.
        ValueError: If the submodules don't start on line 4.
        ValueError: If the submodules header is unexpected.
        ValueError: If the module header is unexpected.
        ValueError: If the toctree doesn't begin as expected.
    """
    rewritten_content = []

    with open(INDEX_FILE, 'r') as file_obj:
        contents = file_obj.read()

    lines = contents.split('\n')
    # Find the title header **and** assert there is only one '==...==' line.
    title_index, = [i for i, line in enumerate(lines)
                    if set(line) == set('=')]
    if title_index != 1:
        raise ValueError('Unexpected title line', title_index)
    if lines[0] != 'ci_diff_helper package':
        raise ValueError('Unexpected title content', lines[0])

    title = '``ci-diff-helper``'
    rewritten_content.append(title)
    rewritten_content.append('=' * len(title))

    # Find the sections **and** assert there are only two '--...--' line.
    submod_index, mod_index = [i for i, line in enumerate(lines)
                               if set(line) == set('-')]
    if submod_index != 4:
        raise ValueError('Unexpected submodules line', submod_index)
    if lines[2:6] != ['', 'Submodules', lines[4], '']:
        raise ValueError('Unexpected submodules header', lines[2:6])
    if lines[mod_index - 1] != 'Module contents':
        raise ValueError('Unexpected module header', lines[mod_index - 1])
    if tuple(lines[mod_index + 1:]) != _EXPECTED_AUTOMODULE_LINES:
        raise ValueError('Unexpected automodule content',
                         lines[mod_index + 1:])

    members_config = '    :members:'
    members = public_members()
    if members:
        members_str = ', '.join(members)
        members_config += ' ' + members_str
    automodule_lines = [
        '',
        '.. automodule:: ci_diff_helper',
        members_config,
        '',
    ]
    rewritten_content.extend(automodule_lines)

    # Make the TOC tree hidden.
    toctree_lines = lines[6:mod_index - 1]
    if toctree_lines[:2] != ['.. toctree::', '']:
        raise ValueError('Unexpected toctree start', toctree_lines[:2])
    toctree_lines.insert(1, '   :hidden:')
    rewritten_content.extend(toctree_lines)

    # Write the new content to a file.
    with open(INDEX_FILE, 'w') as file_obj:
        file_obj.write('\n'.join(rewritten_content))


if __name__ == '__main__':
    main()