from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('tienda', '0008_usuario_cuenta')]

    operations = [
        migrations.AddField(
            model_name='pedido',
            name='tipo_entrega',
            field=models.CharField(
                choices=[('despacho', 'Despacho a domicilio'), ('retiro', 'Retiro en tienda')],
                default='retiro', max_length=20,
            ),
        ),
        migrations.AddField(
            model_name='pedido',
            name='direccion_entrega',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='pedido',
            name='costo_envio',
            field=models.DecimalField(decimal_places=0, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name='pedido',
            name='checkout_token',
            field=models.CharField(blank=True, max_length=64, null=True, unique=True),
        ),
    ]
