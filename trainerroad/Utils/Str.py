import datetime as dt

today = dt.datetime.today()
DURATION = "Duration"
STEADY_STATE = "SteadyState"
POWER = "Power"
TRAINER_ROAD = "TrainerRoad"
WORKOUT = "Workout"
WORKOUT_STR = "workout"
WORKOUT_FILE = "workout_file"
NAME = "name"
DESCRIPTION = "description"
POWER_HIGH = 'PowerHigh'
POWER_LOW = 'PowerLow'
WORKOUT_NAME = "WorkoutName"
WORKOUT_DESC = "WorkoutDescription"
AUTHOR = 'author'
DATE = 'Date'
WARMUP = "Warmup"
COOLDOWN = "Cooldown"
RAMP = "Ramp"
ACTIVITY_ID = "Activity.Id"
DETAILS = 'Details'
INTERVAL = 'intervalData'
ID = 'Id'

USERNAME = 'Username'
PASSWORD = 'Password'
OUTPUT_FILE = f"training_plan_{today.strftime('%d_%m_%Y_%H_%M_%S')}.zip"
TRAINERROAD_USER = 'TRAINERROAD_USER'
TRAINERROAD_PASSWORD = 'TRAINERROAD_PASSWORD'
SUCCESS_MARKDOWN_WARNING = "Status: <font color='green'>Success</font>"
OUTPUT_PATH_MARKDOWN_WARNING = "Output path: <strong><em>{}</em></strong>."
FAIL_MARKDOWN_WARNING = "Status: <font color='red'>Fail</font>"
OUTPUT_FOLDER = 'output'
