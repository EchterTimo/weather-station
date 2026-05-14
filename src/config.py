'''
Logic for reading .env file
'''
from environs import env

env.read_env()

# EMAIL
EMAIL_SMTP_SERVER = env.str('EMAIL_SMTP_SERVER')
EMAIL_SMTP_PORT = env.int('EMAIL_SMTP_PORT', 465)

EMAIL_USERNAME = env.str('EMAIL_USERNAME')
EMAIL_PASSWORD = env.str('EMAIL_PASSWORD')

EMAIL_FROM = env.str('EMAIL_FROM', '') or EMAIL_USERNAME
EMAIL_TO = env.str('EMAIL_TO')

# Thresholds
THRESHOLD_CHECK_INTERVAL = env.int('THRESHOLD_CHECK_INTERVAL', 3)
THRESHOLD_TRIGGER_COOLDOWN = env.int('THRESHOLD_TRIGGER_COOLDOWN', 60)
'''for email notifications to avoid spamming the user with emails'''

# Measure intervals
REGULAR_MEASURE_INTERVAL = env.int('MEASURE_INTERVAL', 30)
LIVE_MEASURE_INTERVAL = env.int('LIVE_MEASURE_INTERVAL', 1)

# UI
UI_TIMEZONE = env.str('UI_TIMEZONE', 'Europe/Berlin')
