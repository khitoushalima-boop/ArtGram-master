from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.IntegerField()),
                ('sender_id', models.IntegerField()),
                ('artwork_id', models.IntegerField(blank=True, null=True)),
                ('type', models.CharField(choices=[('LIKE', 'Like'), ('COMMENT', 'Comment'), ('FOLLOW', 'Follow')], max_length=10)),
                ('message', models.TextField()),
                ('is_read', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
