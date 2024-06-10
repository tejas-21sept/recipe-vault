from app.extensions import db


def toggle_key_checks(enable: bool):
    """
    Toggle foreign key checks in the database.

    Args:
        enable (bool): True to enable foreign key checks, False to disable.
    """
    if enable:
        db.session.execute("SET FOREIGN_KEY_CHECKS=1")
    else:
        db.session.execute("SET FOREIGN_KEY_CHECKS=0")
