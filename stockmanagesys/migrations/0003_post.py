# Generated by Django 4.1.7 on 2023-04-18 21:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stockmanagesys', '0002_category_rename_issue_to_stock_updated_by_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='post',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
            ],
        ),
    ]
