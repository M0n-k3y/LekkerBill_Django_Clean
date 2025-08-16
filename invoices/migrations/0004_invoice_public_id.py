# This is a manually corrected migration file to add a public_id to Invoices.

from django.db import migrations, models
import uuid


def gen_uuid(apps, schema_editor):
    """Assign a unique UUID to each existing Invoice."""
    Invoice = apps.get_model('invoices', 'Invoice')
    for row in Invoice.objects.all():
        row.public_id = uuid.uuid4()
        row.save(update_fields=['public_id'])


class Migration(migrations.Migration):
    dependencies = [
        ('invoices', '0003_quote_valid_until_alter_inventoryitem_description_and_more'),
        # Make sure this matches your previous migration
    ]

    operations = [
        # Step 1: Add the field but allow it to be null temporarily.
        migrations.AddField(
            model_name='invoice',
            name='public_id',
            field=models.UUIDField(null=True, editable=False),
        ),
        # Step 2: Run our custom Python code to populate unique UUIDs for existing rows.
        migrations.RunPython(gen_uuid, reverse_code=migrations.RunPython.noop),
        # Step 3: Now that all rows have a unique value, alter the field to be non-nullable and unique.
        migrations.AlterField(
            model_name='invoice',
            name='public_id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
        ),
    ]