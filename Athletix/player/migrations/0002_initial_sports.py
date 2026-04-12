# Generated migration to add initial sports data

from django.db import migrations


def create_initial_sports(apps, schema_editor):
    Sport = apps.get_model('player', 'Sport')
    
    sports = [
        {'name': 'Cricket', 'description': 'Bat and ball game played between two teams', 'icon': '🏏'},
        {'name': 'Football', 'description': 'Team sport played with a spherical ball', 'icon': '⚽'},
        {'name': 'Basketball', 'description': 'Team sport played on a rectangular court', 'icon': '🏀'},
        {'name': 'Tennis', 'description': 'Racket sport played individually or in pairs', 'icon': '🎾'},
        {'name': 'Badminton', 'description': 'Racket sport using a shuttlecock', 'icon': '🏸'},
        {'name': 'Swimming', 'description': 'Individual or team sport in water', 'icon': '🏊'},
        {'name': 'Athletics', 'description': 'Track and field events', 'icon': '🏃'},
        {'name': 'Hockey', 'description': 'Team sport played with sticks and a ball', 'icon': '🏑'},
        {'name': 'Volleyball', 'description': 'Team sport with a ball over a net', 'icon': '🏐'},
        {'name': 'Table Tennis', 'description': 'Racket sport played on a table', 'icon': '🏓'},
        {'name': 'Boxing', 'description': 'Combat sport involving punching', 'icon': '🥊'},
        {'name': 'Wrestling', 'description': 'Combat sport involving grappling', 'icon': '🤼'},
        {'name': 'Kabaddi', 'description': 'Contact team sport from India', 'icon': '🤸'},
        {'name': 'Cycling', 'description': 'Sport using bicycles', 'icon': '🚴'},
        {'name': 'Gymnastics', 'description': 'Sport requiring balance and flexibility', 'icon': '🤸‍♀️'},
    ]
    
    for sport_data in sports:
        Sport.objects.create(**sport_data)


def remove_initial_sports(apps, schema_editor):
    Sport = apps.get_model('player', 'Sport')
    Sport.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('player', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_initial_sports, remove_initial_sports),
    ]
