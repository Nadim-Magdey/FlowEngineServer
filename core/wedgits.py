# widgets.py
from django import forms
from django.utils.safestring import mark_safe

class FlowEditorWidget(forms.Widget):
    class Media:
        js = ('admin/js/flows_editor.js',)

    def render(self, name, value, attrs=None, renderer=None):
        if value is None:
            value = '{}'
        html = f'''
        <div id="flows-editor-container"></div>
        <textarea name="{name}" id="id_{name}" style="display:none;">{value}</textarea>
        '''
        return mark_safe(html)
