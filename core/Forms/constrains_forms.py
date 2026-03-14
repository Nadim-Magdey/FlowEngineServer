# admin.py
from django import forms
from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from ..models import FlowConstraint, Service, FixedFlow, OptionalFlow

class FlowConstraintForm(forms.ModelForm):
    left_flow_choice = forms.ChoiceField(label="Left Flow")
    right_flow_choice = forms.ChoiceField(label="Right Flow")

    class Meta:
        model = FlowConstraint
        fields = []  # <-- completely ignore all model fields
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Combine all flows
        all_flows = [f.name for f in Service.objects.all()]
        all_flows += [f.name for f in FixedFlow.objects.all()]
        all_flows += [f.name for f in OptionalFlow.objects.all()]

        choices = [(name, name) for name in all_flows]
        self.fields['left_flow_choice'].choices = choices
        self.fields['right_flow_choice'].choices = choices

        if self.instance.pk:
            self.fields['left_flow_choice'].initial = self.instance.left_flow.name
            self.fields['right_flow_choice'].initial = self.instance.right_flow.name
            
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Map names back to objects
        left_name = self.cleaned_data['left_flow_choice']
        right_name = self.cleaned_data['right_flow_choice']

        instance.left_flow = (
            Service.objects.filter(name=left_name).first() or
            FixedFlow.objects.filter(name=left_name).first() or
            OptionalFlow.objects.filter(name=left_name).first()
        )

        instance.right_flow = (
            Service.objects.filter(name=right_name).first() or
            FixedFlow.objects.filter(name=right_name).first() or
            OptionalFlow.objects.filter(name=right_name).first()
        )
        
        if commit:
            instance.save()
        return instance
