import csv
import json
from django.http import HttpResponse
from django.urls import path
from django.shortcuts import render, redirect
from django.contrib import messages


class FlowIOAdminMixin:

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('export-flows/', self.admin_site.admin_view(self.export_flows), name=f'{self.model._meta.model_name}_export'),
            path('import-flows/', self.admin_site.admin_view(self.import_flows), name=f'{self.model._meta.model_name}_import'),
        ]
        return custom_urls + urls

    # ✅ EXPORT ONLY THIS MODEL
    def export_flows(self, request):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{self.model._meta.model_name}_flows.csv"'

        writer = csv.writer(response)
        writer.writerow(['id', 'flows'])

        for obj in self.model.objects.all():
            writer.writerow([
                obj.id,
                json.dumps(obj.flows)
            ])

        return response

    # ✅ IMPORT ONLY THIS MODEL
    def import_flows(self, request):
        if request.method == "POST":
            file = request.FILES.get('file')

            if not file:
                self.message_user(request, "No file uploaded", level=messages.ERROR)
                return redirect("..")

            decoded = file.read().decode('utf-8').splitlines()
            reader = csv.DictReader(decoded)

            updated = 0

            for row in reader:
                try:
                    obj_id = int(row['id'])
                    flows = json.loads(row['flows'])
                except Exception:
                    continue

                try:
                    obj = self.model.objects.get(id=obj_id)
                except self.model.DoesNotExist:
                    continue

                obj.flows = flows
                obj.save()
                updated += 1

            self.message_user(request, f"{updated} flows updated successfully")
            return redirect("..")

        return render(request, "admin/import_flows.html")
