import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('core', '0001_initial'),
        ('vagas', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='MatchScore',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('score', models.FloatField(default=0.0)),
                ('breakdown', models.JSONField(default=dict)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='match_scores', to='core.usuario')),
                ('vaga', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='match_scores', to='vagas.vagas')),
            ],
            options={
                'unique_together': {('usuario', 'vaga')},
            },
        ),
    ]
