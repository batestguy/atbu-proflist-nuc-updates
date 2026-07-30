"""
atbu_icons.py — Material Design icon codepoints as plain integer constants.

This module avoids Flet's _IconsProxy class which PyInstaller cannot
correctly freeze.  All values were extracted from Flet 0.86.3.

Usage:
    from atbu_icons import (
        DASHBOARD_ROUNDED, SEARCH, LOCK_OUTLINE, …
    )
"""

# Material Design icon codepoints (Flet 0.86.3)
DASHBOARD_ROUNDED      = 67357
DASHBOARD              = 67351
PEOPLE_OUTLINE_ROUNDED = 71044
PEOPLE                 = 71037
PERSON_ADD_OUTLINED    = 71119
PERSON_ADD             = 71106
FILE_DOWNLOAD_OUTLINED = 68339
FILE_DOWNLOAD          = 68330
INFO_OUTLINE_ROUNDED   = 69376
INFO                   = 69374
SETTINGS_OUTLINED      = 72298
SETTINGS               = 72245
LOCK_OPEN              = 69951
LOCK_OUTLINE           = 69955
SEARCH                 = 72141
CONTENT_COPY           = 67134
EDIT_OUTLINED          = 67911
SEARCH_OFF             = 72142
UPLOAD_FILE            = 73771
FOLDER_OPEN            = 68623
