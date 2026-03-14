from django import forms
from ..models import FixedFlow, OptionalFlow, Service, FLOW_SCHEMA, INPUT_SCHEMA
import json
import jsonschema
from django.core.exceptions import ValidationError

class OptionalFlowForm(forms.ModelForm):
    flows_json = forms.CharField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = OptionalFlow
        fields = ('name','is_active','order',"users")

    class Media:
        js = (
            'admin/js/flows_editor.js',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance.pk:
            self.fields['flows_json'].initial = json.dumps(
                self.instance.flows or {}, indent=2
            )

    def clean(self):
        cleaned_data = super().clean()
        
        flows_data = cleaned_data.get('flows_json', '{}')
        try:
            flows = json.loads(flows_data)
            jsonschema.validate(instance=flows, schema=FLOW_SCHEMA)
        except Exception as e:
            raise ValidationError(f"Invalid flows schema: {e}")
        
        cleaned_data['flows'] = flows
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.flows = self.cleaned_data.get('flows', {})
        if commit:
            instance.save()
        return instance

    