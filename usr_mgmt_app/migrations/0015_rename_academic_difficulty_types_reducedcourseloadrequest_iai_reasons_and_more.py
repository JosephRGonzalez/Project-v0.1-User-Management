# Generated by Django 5.1.6 on 2025-04-14 20:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('usr_mgmt_app', '0014_reducedcourseloadrequest'),
    ]

    operations = [
        migrations.RenameField(
            model_name='reducedcourseloadrequest',
            old_name='academic_difficulty_types',
            new_name='iai_reasons',
        ),
        migrations.RemoveField(
            model_name='reducedcourseloadrequest',
            name='courses_to_drop',
        ),
        migrations.AddField(
            model_name='reducedcourseloadrequest',
            name='academic_type',
            field=models.CharField(blank=True, choices=[('IAI', 'Initial Adjustment Issues'), ('ICLP', 'Improper Course Level Placement')], max_length=10, null=True),
        ),
        migrations.AddField(
            model_name='reducedcourseloadrequest',
            name='course_to_drop_1',
            field=models.CharField(default='', max_length=20),
        ),
        migrations.AddField(
            model_name='reducedcourseloadrequest',
            name='course_to_drop_2',
            field=models.CharField(blank=True, default='', max_length=20),
        ),
        migrations.AddField(
            model_name='reducedcourseloadrequest',
            name='course_to_drop_3',
            field=models.CharField(blank=True, default='', max_length=20),
        ),
        migrations.AddField(
            model_name='reducedcourseloadrequest',
            name='final_type',
            field=models.CharField(blank=True, choices=[('non_thesis', 'Non-Thesis Track'), ('thesis', 'Thesis/Dissertation Track')], max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='reducedcourseloadrequest',
            name='thesis_hours',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='reducedcourseloadrequest',
            name='reason',
            field=models.CharField(choices=[('academic', 'Academic Difficulty'), ('medical', 'Medical Reason'), ('final', 'Final Semester')], max_length=10),
        ),
        migrations.AlterField(
            model_name='reducedcourseloadrequest',
            name='student_id',
            field=models.CharField(max_length=7),
        ),
        migrations.AlterField(
            model_name='reducedcourseloadrequest',
            name='total_credit_hours_after_drop',
            field=models.PositiveIntegerField(),
        ),
    ]
