# Generated by Django 3.0.6 on 2020-05-17 19:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Erp', '0003_auto_20200517_1853'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='deploy',
            options={'ordering': ['-deployid'], 'verbose_name_plural': '调配'},
        ),
        migrations.AlterModelOptions(
            name='inventory',
            options={'ordering': ['-inventoryId'], 'verbose_name_plural': '库存'},
        ),
        migrations.AlterModelOptions(
            name='material',
            options={'ordering': ['-materialId'], 'verbose_name_plural': '物料'},
        ),
        migrations.AlterModelOptions(
            name='order',
            options={'ordering': ['-orderId'], 'verbose_name_plural': 'Bom记录'},
        ),
    ]
