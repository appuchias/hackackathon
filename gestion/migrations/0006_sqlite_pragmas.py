from django.db import migrations, models


class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        ("gestion", "0005_alter_token_token"),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            PRAGMA journal_mode=WAL;
            PRAGMA synchronous=normal;
            PRAGMA busy_timeout=5000;
            PRAGMA foreign_keys=ON;
            """,
            reverse_sql="""
            PRAGMA journal_mode=DELETE;
            PRAGMA synchronous=FULL;
            PRAGMA busy_timeout=0;
            PRAGMA foreign_keys=OFF;
            """,
        ),
    ]
