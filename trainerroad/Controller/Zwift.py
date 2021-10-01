import logging
import os
from collections.abc import Iterable

from ..Model.TrainerRoad import TrainerRoad
from ..Model.Workout import Workout
from ..Utils.Str import *


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
    def __init__(self, username: str, password: str, output_folder: str):
        self.trainer = TrainerRoad(username=username, password=password)
        self.trainer.connect()
        self.workout_manager = Workout()
        self.output_path = output_folder

        try:
            os.makedirs(self.output_path)
            logging.info(f"Folder {self.output_path} does not exist creating path")
        except FileExistsError:
            pass

    async def export_training_plan(self, include_date: bool, start_date: str = "12-25-2020",
                                   end_date: str = "09-25-2023"):
        calendar = self.trainer.get_training_plans(start_date=start_date, end_date=end_date)
        workouts = list(set(calendar[ACTIVITY_ID]))
        response = await self.trainer.get_workouts_details(workouts=workouts)
        plan_dict = create_plan_dictionary(response)

        for date, workout_id in zip(calendar[DATE], calendar[ACTIVITY_ID]):
            workout = plan_dict.get(workout_id)
            if bool(workout):
                workout_details = workout.get(DETAILS)
                workout_interval = workout.get(INTERVAL)
                workout_name = workout_details.get(WORKOUT_NAME)

                if bool(workout_interval) and bool(workout_name):
                    try:
                        doc = self.workout_manager.convert_workout(interval=workout_interval,
                                                                   workout_details=workout_details)

                        doc_str = doc.toprettyxml(indent="\t")

                        filename = f"{date}_{workout_name}.zwo" if include_date else f"{workout_name}.zwo"
                        out_path = os.path.join(self.output_path, filename)
                        try:
                            with open(out_path, "w") as f:
                                f.write(doc_str)
                        except Exception as e:
                            logging.error(f"Error saving workout {filename}: {str(e)}")
                            pass
                    except RuntimeError:
                        logging.error(workout_name)
                else:
                    logging.error(workout_name)
