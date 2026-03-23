from django import forms
from django.utils.safestring import mark_safe

class DualListWidget(forms.SelectMultiple):
    class Media:
        js = ('admin/js/flow_constrants.js',)
        css = {'all': ('admin/css/dual_list.css',)}

    def render(self, name, value, attrs=None, renderer=None):
        if value is None:
            value = []

        # ✅ make value a set for fast lookup
        selected_set = set(value)

        left_options = []
        right_options = []

        for val, label in self.choices:
            option_html = f'<option value="{val}">{label}</option>'

            if str(val) in selected_set:
                right_options.append(option_html)   # ✅ goes to right
            else:
                left_options.append(option_html)    # ✅ stays left

        html = f"""
        <div class="dual-listbox">
            <div>
                <label>Available Flows</label><br/>
                <select multiple class="dual-left" size="10">
                    {''.join(left_options)}
                </select>
            </div>

            <div class="dual-list-buttons">
                <button type="button" class="dual-move" data-direction="right">&gt;&gt;</button><br/>
                <button type="button" class="dual-move" data-direction="left">&lt;&lt;</button>
            </div>

            <div>
                <label>Selected Flows</label><br/>
                <select multiple name="{name}" class="dual-right" size="10">
                    {''.join(right_options)}
                </select>
            </div>
        </div>
        """

        return mark_safe(html)
