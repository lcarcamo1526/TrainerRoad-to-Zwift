import datetime as dt

today = dt.datetime.today()
DURATION = "Duration"
STEADY_STATE = "SteadyState"
POWER = "Power"
TRAINER_ROAD = "TrainerRoad"
WORKOUT = "Workout"
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
ACTIVITY_ID = "Activity.Id"
DETAILS = 'Details'
INTERVAL = 'intervalData'
ID = 'Id'
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_3) AppleWebKit/605.1.15 (KHTML, like Gecko) " \
             "Version/14.1 Safari/605.1.15 "

OUTPUT_FILE = f"training_plan_{today.strftime('%d_%m_%Y_%H_%M_%S')}.zip"
