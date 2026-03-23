from django import forms
from ..models import FixedFlow, FLOW_SCHEMA
import json
import jsonschema
from django.core.exceptions import ValidationError


class FixedFlowsForm(forms.ModelForm):
    flows_json = forms.CharField(widget=forms.HiddenInput(), required=False)
    notify_condition_json = forms.CharField(widget=forms.HiddenInput(), required=False)
    notify_variables_json = forms.CharField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = FixedFlow
        fields = ('name', 'is_active', 'order', 'users', "group")

    class Media:
        js = (
            'admin/js/flows_editor.js',
            'admin/js/notification_editor.js',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance.pk:
            self.fields['flows_json'].initial = json.dumps(
                self.instance.flows or {}, indent=2
            )
            self.fields['notify_condition_json'].initial = json.dumps(
                self.instance.notify_condition or {}, indent=2
            )
            self.fields['notify_variables_json'].initial = json.dumps(
                self.instance.notify_variables or [], indent=2
            )

    def clean(self):
        cleaned_data = super().clean()

        # ✅ Validate flows schema
        flows_data = cleaned_data.get('flows_json', '{}')
        try:
            flows = json.loads(flows_data)
            jsonschema.validate(instance=flows, schema=FLOW_SCHEMA)
        except Exception as e:
            raise ValidationError(f"Invalid flows schema: {e}")

        cleaned_data['flows'] = flows

        # ✅ Notification fields
        try:
            notify_condition = json.loads(
                cleaned_data.get('notify_condition_json', '{}')
            )
            notify_variables = json.loads(
                cleaned_data.get('notify_variables_json', '[]')
            )
        except Exception:
            raise ValidationError("Invalid notification data")

        cleaned_data['notify_condition'] = notify_condition
        cleaned_data['notify_variables'] = notify_variables

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)

        instance.flows = self.cleaned_data.get('flows', {})
        instance.notify_condition = self.cleaned_data.get('notify_condition', {})
        instance.notify_variables = self.cleaned_data.get('notify_variables', [])

        if commit:
            instance.save()
            self.save_m2m()

        return instance
