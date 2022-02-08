"""First migration

Migration ID: b833938fe6d0
Revises: 
Creation Date: 2022-02-08 18:21:05.811353

"""

from emmett.orm import migrations


class Migration(migrations.Migration):
    revision = 'b833938fe6d0'
    revises = None

    def up(self):
        self.create_table(
            'games',
            migrations.Column('id', 'id'),
            migrations.Column('last_played_date', 'datetime'),
            migrations.Column('correct_number', 'integer'),
            migrations.Column('finished', 'boolean'),
            primary_keys=['id'])
        self.create_table(
            'guesseds',
            migrations.Column('id', 'id'),
            migrations.Column('number', 'integer'),
            migrations.Column('game', 'reference games', ondelete='CASCADE'),
            primary_keys=['id'])

    def down(self):
        self.drop_table('guesseds')
        self.drop_table('games')
