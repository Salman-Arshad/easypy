from django import template
from django.utils.safestring import mark_safe

register = template.Library()

root = """
<div style="margin-left: 0.6em;">
    <span class="badge badge-secondary custom-expand mr-2" onclick="toggleTree(this, 'ul%(abs_path)s');">-</span>
    <i class="fas fa-folder"></i>
    <span id="%(abs_path)s" class="file file-dir" directory="true">%(name)s</span>
</div>
<ul id="ul%(abs_path)s">%(html_children)s</ul>
"""

directory = """<li class="file container">               
    <div>
        <span class="badge badge-secondary custom-expand mr-2" onclick="toggleTree(this, 'ul%(abs_path)s');">-</span>
        <i class="fas fa-folder"></i>
        <span id="%(abs_path)s" class="file-dir" directory="true">%(name)s</span>
    </div>
    <ul id="ul%(abs_path)s">%(html_children)s</ul>
</li>
"""

simple_file = """
<li class="file">               
    <div>
        <span class="badge badge-light custom-expand mr-2"></span>
        <i class="fas fa-file file-stroke"></i>
        <span id="%(abs_path)s" class="file-dir">%(name)s</span>
    </div>
</li>
"""


def get_node(dd):
    if dd['is_dir']:
        dd['html_children'] = ''.join([get_node(i) for i in dd['children']])
        return directory % dd
    return simple_file % dd


@register.filter(name='as_li', is_safe=True)
def tree_as_li(tree):
    tree['html_children'] = ''.join([get_node(i) for i in tree['children']])
    return mark_safe(root % tree)

