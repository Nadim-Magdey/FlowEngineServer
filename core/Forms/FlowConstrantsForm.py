# from django import forms
# from django.contrib.contenttypes.models import ContentType

# from widgets.flow_constrains_widget import DualListWidget
# from ..models import FlowConstraint, FlowConstraintGroup, OptionalFlow, FixedFlow, Service

# class FlowConstraintForm(forms.ModelForm):
#     flows = forms.MultipleChoiceField(
#         choices=[],
#         widget=DualListWidget
#     )

#     class Meta:
#         model = FlowConstraintGroup
#         fields = ['name']

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         # Gather all flows
#         optional_flows = OptionalFlow.objects.all()
#         fixed_flows = FixedFlow.objects.all()
#         services = Service.objects.all()
#         choices = [(f"{type(f).__name__}:{f.id}", str(f)) for f in list(optional_flows)+list(fixed_flows)+list(services)]
#         self.fields['flows'].choices = choices

#         if self.instance and self.instance.pk and self.instance.flows:
#             self.initial['flows'] = self.instance.flows

#     def save(self, commit=True):
#         group = super().save(commit=False)

#         selected_flows = self.cleaned_data['flows']

#         # ✅ store flows in group
#         group.flows = selected_flows

#         if group.pk is None:
#             group.save()
#         else:
#             group.save()  # save updates

#         # --- remove old constraints for this group ---
#         FlowConstraint.objects.filter(group=group).delete()

#         # --- create new constraints ---
#         def parse_choice(val):
#             type_name, obj_id = val.split(":")
#             model = {
#                 'OptionalFlow': OptionalFlow,
#                 'FixedFlow': FixedFlow,
#                 'Service': Service
#             }[type_name]
#             return model.objects.get(id=int(obj_id))

#         objs = [parse_choice(x) for x in selected_flows]

#         ct_cache = {}
#         def get_ct(obj):
#             model = type(obj)
#             if model not in ct_cache:
#                 ct_cache[model] = ContentType.objects.get_for_model(model)
#             return ct_cache[model]

#         for left in objs:
#             for right in objs:
#                 if left == right:
#                     continue
#                 FlowConstraint.objects.create(
#                     group=group,
#                     left_content_type=get_ct(left),
#                     left_object_id=left.id,
#                     right_content_type=get_ct(right),
#                     right_object_id=right.id
#                 )

#         return group

    
#     def save_m2m(self):
#         # REQUIRED by Django admin
#         pass