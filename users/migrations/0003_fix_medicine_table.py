# Fix migration: the actual DB table (users_medicine) was created by an older
# migration history with different columns (name, stock, category, is_available,
# created_at) while the current Django state (from 0002) expects the new schema
# (name_en, name_ar, description, price, image).
#
# This migration ONLY touches the real database using RunSQL — no state_operations
# — because Django's ORM state already matches the new model after 0002.

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_medicine_disease_symptoms_ar_disease_symptoms_en_and_more'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
                CREATE TABLE IF NOT EXISTS users_medicine_new (
                    id    INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                    name_en     varchar(150) NOT NULL DEFAULT '',
                    name_ar     varchar(150) NULL,
                    description TEXT NULL,
                    price       decimal      NOT NULL DEFAULT 0,
                    image       varchar(100) NULL
                );
                INSERT INTO users_medicine_new (id, description, price)
                    SELECT id, description, price FROM users_medicine;
                DROP TABLE users_medicine;
                ALTER TABLE users_medicine_new RENAME TO users_medicine;
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]
