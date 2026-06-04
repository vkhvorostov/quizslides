from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_slide_content'),
    ]

    operations = [
        migrations.AddField(
            model_name='session',
            name='current_slide_number',
            field=models.IntegerField(default=1),
        ),
        migrations.CreateModel(
            name='PollVote',
            fields=[
                ('id_poll_vote', models.AutoField(primary_key=True, serialize=False)),
                ('id_answer_option', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='poll_votes',
                    to='core.answeroption',
                )),
                ('id_member', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='poll_votes',
                    to='core.member',
                )),
                ('id_slide', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='poll_votes',
                    to='core.slide',
                )),
            ],
            options={
                'constraints': [
                    models.UniqueConstraint(
                        fields=('id_slide', 'id_member'),
                        name='unique_poll_vote_per_slide',
                    ),
                ],
            },
        ),
    ]
