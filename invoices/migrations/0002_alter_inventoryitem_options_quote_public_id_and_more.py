# F:/Python Apps/LekkerBill_Django_Clean/invoices/migrations/0002_alter_inventoryitem_options_quote_public_id_and_more.py

# This is a manually corrected migration file to prevent unique constraint errors.

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid

# This custom function will be run to give each existing quote a unique ID.
def gen_uuid(apps, schema_editor):
    Quote = apps.get_model('invoices', 'Quote')
    for row in Quote.objects.all():
        row.public_id = uuid.uuid4()
        row.save(update_fields=['public_id'])


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('invoices', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='inventoryitem',
            options={'ordering': ['name'], 'verbose_name': 'Inventory Item', 'verbose_name_plural': 'Inventory Items'},
        ),
        migrations.AlterField(
            model_name='profile',
            name='invoice_next_number',
            field=models.IntegerField(default=1, help_text='The next number to be used for a new invoice.'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='invoice_prefix',
            field=models.CharField(default='INV-', help_text='The prefix for your invoice numbers (e.g., INV-).', max_length=10),
        ),
        migrations.AlterField(
            model_name='profile',
            name='quote_next_number',
            field=models.IntegerField(default=1, help_text='The next number to be used for a new quote.'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='quote_prefix',
            field=models.CharField(default='QTE-', help_text='The prefix for your quote numbers (e.g., QTE-).', max_length=10),
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField()),
                ('is_read', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('link', models.URLField(blank=True, help_text='A link to the relevant object (e.g., a quote).', null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        # --- THE FIX for Quote.public_id ---
        # Step 1: Add the field but allow it to be null temporarily.
        migrations.AddField(
            model_name='quote',
            name='public_id',
            field=models.UUIDField(null=True, editable=False),
        ),
        # Step 2: Run our custom Python code to populate unique UUIDs for existing rows.
        migrations.RunPython(gen_uuid, reverse_code=migrations.RunPython.noop),
        # Step 3: Now that all rows have a unique value, alter the field to be non-nullable and unique.
        migrations.AlterField(
            model_name='quote',
            name='public_id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
        ),
    ]