# Generated by Django 3.0.6 on 2020-05-17 18:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Erp', '0002_auto_20200517_1848'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='ddl',
            field=models.DateField(verbose_name='完工日期'),
        ),
    ]