import logging
import os
import traceback
import zipfile
from collections.abc import Iterable

from ..Model.TrainerRoad import TrainerRoad
from ..Model.Workout import Workout
from ..Utils.Str import *


def gen_zip_from_path(dir_to_archive, archive_filename):
    ziph = zipfile.ZipFile(archive_filename, 'w', zipfile.ZIP_DEFLATED)
    for root, dirs, files in os.walk(dir_to_archive):
        for file in files:
            if file != archive_filename:
                ziph.write(os.path.join(root, file))
    ziph.close()


def create_plan_dictionary(response: Iterable) -> dict:
    saved_workouts = {}
    if bool(response):
        for workout in response:
            workout_info = workout.get(WORKOUT)
            if bool(workout_info):
                workout_details = workout_info.get(DETAILS)
                workout_id = workout_details.get(ID)
                workout_interval = workout_info.get(INTERVAL)

                if bool(workout_id):
                    workout_id = int(workout_id)
                    saved_workouts[workout_id] = {
                        DETAILS: workout_details,
                        INTERVAL: workout_interval,

                    }
    return saved_workouts


class Zwift:
    def __init__(self, username: str, password: str, output_folder: str = OUTPUT_FOLDER):
        self.trainer = TrainerRoad(username=username, password=password)
        # self.trainer.connect()
        self.workout_manager = Workout()
        self.output_path = output_folder
        self.temp_path = os.path.join(self.output_path, 'Zwift')
        self.zipfile = None
        self.logger = logging.getLogger('')

        try:
            os.makedirs(self.temp_path)
            logging.info(f"Folder {self.output_path} does not exist creating path")
        except FileExistsError:
            pass

    async def export_training_plan(self, include_date: bool, start_date: str = None,
                                   end_date: str = None, compress=False, offset_years=3) -> bool:
        try:
            today = dt.datetime.today()
            if bool(start_date) is False:
                start_date = today.strftime("%m-%d-%Y")

            if bool(end_date) is False:
                result = today + dt.timedelta(days=365 * offset_years)
                end_date = result.strftime("%m-%d-%Y")
            calendar = self.trainer.get_training_plans(start_date=start_date, end_date=end_date)
            workouts = list(set(calendar[ACTIVITY_ID]))
            logging.info(workouts)
            response = await self.trainer.get_workouts_details(workouts=workouts)
            plan_dict = create_plan_dictionary(response)

            for date, workout_id in zip(calendar[DATE], calendar[ACTIVITY_ID]):
                workout_plan = plan_dict.copy()
                workout = workout_plan.get(workout_id)

                if bool(workout):
                    workout_details = workout.get(DETAILS)
                    workout_interval = workout.get(INTERVAL)
                    logging.info(workout_interval)

                    date = date.strftime("%Y-%m-%d")
                    workout_name = workout_details.get(WORKOUT_NAME)
                    if include_date:
                        new_workout_details = workout_details.copy()
                        new_workout_name = f"{date} {workout_name}"
                        new_workout_details[WORKOUT_NAME] = new_workout_name
                        workout_details = new_workout_details
                        workout_name = new_workout_name

                    if bool(workout_interval):
                        try:
                            doc = self.workout_manager.convert_workout(interval=workout_interval,
                                                                       workout_details=workout_details)

                            doc_str = doc.toprettyxml(indent="\t")

                            filename = f"{workout_name}.zwo"
                            out_path = os.path.join(self.temp_path, filename)
                            try:
                                with open(out_path, "w") as f:
                                    f.write(doc_str)
                            except Exception as e:
                                logging.error(f"Error saving workout {filename}: {str(e)} {traceback.format_exc()} ")
                                pass
                        except RuntimeError as e:
                            logging.error(e)
                            logging.error(workout_name)
                    else:
                        logging.error(workout_name)

            if compress:
                self.zipfile = os.path.join(self.output_path, OUTPUT_FILE)
                try:
                    gen_zip_from_path(dir_to_archive=self.temp_path, archive_filename=self.zipfile)
                    logging.warning(f"Successfully compressed workout, saved in: {self.zipfile}")
                except Exception as e:
                    logging.error(f"Failed to save Zip File: {self.zipfile} + {e}")

            return True

        except Exception as e:
            logging.error(e)
            return False
