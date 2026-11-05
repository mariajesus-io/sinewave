from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [('tienda', '0007_producto_foto'), migrations.swappable_dependency(settings.AUTH_USER_MODEL)]

    operations = [
        migrations.AddField(
            model_name='usuario',
            name='cuenta',
            field=models.OneToOneField(
                blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL,
                related_name='cliente', to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
