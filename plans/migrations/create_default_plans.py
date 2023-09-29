from django.db import migrations, models
import json

def create_default_plans(apps, schema_editor):
    """
    Creates Default Plans - Basic, Premium, Enterprise if they do not already exist.
    """
    Plan = apps.get_model('plans', 'Plan')
    plans_to_create = []

    if not Plan.objects.filter(name="Basic").exists():
        basic_plan_data = {
            "name": "Basic",
            "thumbnail_sizes": [
                {
                    "height": 200,
                    "width": 200
                }
            ],
            "include_original_link": False,
            "generate_expiring_links": False
        }
        plans_to_create.append(Plan(**basic_plan_data))

    if not Plan.objects.filter(name="Premium").exists():
        premium_plan_data = {
            "name": "Premium",
            "thumbnail_sizes": [
                {
                    "height": 200,
                    "width": 200
                },
                {
                    "height": 400,
                    "width": 400
                }
            ],
            "include_original_link": True,
            "generate_expiring_links": False
        }
        plans_to_create.append(Plan(**premium_plan_data))

    if not Plan.objects.filter(name="Enterprise").exists():
        enterprise_plan_data = {
            "name": "Enterprise",
            "thumbnail_sizes": [
                {
                    "height": 200,
                    "width": 200
                },
                {
                    "height": 400,
                    "width": 400
                }
            ],
            "include_original_link": True,
            "generate_expiring_links": True
        }
        plans_to_create.append(Plan(**enterprise_plan_data))

    Plan.objects.bulk_create(plans_to_create)
    
class Migration(migrations.Migration):
    dependencies = [
        ('plans', '0001_initial')
    ]

    operations = [
        migrations.RunPython(create_default_plans),
    ]
