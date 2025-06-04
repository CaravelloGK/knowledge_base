from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('docs', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='document',
            name='status',
            field=models.CharField(
                choices=[('active', 'Действующая редакция'), ('obsolete', 'Утратил силу')],
                default='active',
                max_length=10,
                verbose_name='Статус'
            ),
        ),
    ] 