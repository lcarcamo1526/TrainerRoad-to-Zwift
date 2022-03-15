import logging
from collections.abc import Iterable
from collections.abc import Mapping
from xml.dom import minidom
from xml.dom.minidom import Element

from trainerroad.Utils.Str import *


class Workout:
    def __init__(self):
        pass

    def add_workout_to_document(self, workouts: Iterable, document: minidom.Document, section, parent_section):
        """

        :param workouts:
        :param document:
        :param section:
        :param parent_section:
        :return:
        """
        workouts_ = workouts[1:]
        for index, interval in enumerate(workouts_):
            cooldown = index == len(workouts_) - 1
            warmup = index == 0
            self.build_workout(document=document, section=section, interval=interval, warmup=warmup,
                               cooldown=cooldown)
            parent_section.appendChild(section)

    def build_workout(self, document, section, interval: dict, cooldown=False, warmup=False):
        """

        :param document:
        :param section:
        :param interval:
        :param cooldown:
        :param warmup:
        :return:
        """
        end = int(interval.get("End"))
        start = int(interval.get("Start"))
        power = str(float(interval.get("StartTargetPowerPercent")) / 100)
        duration = str(end - start)
        new_interval = None

        if cooldown is False and warmup is False:
            steady_interval = document.createElement(STEADY_STATE)
            steady_interval.setAttribute(DURATION, duration)
            steady_interval.setAttribute(POWER, power)
            new_interval = steady_interval

        elif cooldown and warmup is False:
            cooldown_interval = document.createElement(COOLDOWN)
            cooldown_interval.setAttribute(DURATION, duration)
            cooldown_interval.setAttribute(POWER_HIGH, power)
            # todo set values from previous interval (if exists)
            cooldown_interval.setAttribute(POWER_LOW, power)
            new_interval = cooldown_interval

        elif cooldown is False and warmup:
            warmup_interval = document.createElement(WARMUP)
            warmup_interval.setAttribute(DURATION, duration)
            warmup_interval.setAttribute(POWER_HIGH, power)
            warmup_interval.setAttribute(POWER_LOW, power)
            new_interval = warmup_interval
        else:
            logging.info(
                f" Warmup: {warmup} Cooldown: {cooldown} Power: {power}, Start: {start}, End: {end}, Duration {duration}")
            steady_interval = document.createElement(STEADY_STATE)
            steady_interval.setAttribute(DURATION, duration)
            steady_interval.setAttribute(POWER, power)
            new_interval = steady_interval

        section.appendChild(new_interval)

        return section

    def add_workout_details(self, details, section: Element, document: minidom.Document):
        """

        :param details:
        :param section:
        :param document:
        :return:
        """
        workout_name = details.get(WORKOUT_NAME)
        description = details.get(WORKOUT_DESC)
        author_section = document.createElement(AUTHOR)
        author_section.appendChild(document.createTextNode(TRAINER_ROAD))
        description_section = document.createElement(DESCRIPTION)
        description_section.appendChild(document.createTextNode(description))
        name_section = document.createElement(NAME)
        name_section.appendChild(document.createTextNode(workout_name))

        section.appendChild(author_section)
        section.appendChild(description_section)
        section.appendChild(name_section)

    def convert_workout(self, interval: Iterable, workout_details: Mapping) -> minidom.Document:
        """

        :param interval:
        :param workout_details:
        :return:
        """
        document = minidom.Document()
        workout_file = document.createElement(WORKOUT_FILE)
        workout_section = document.createElement(WORKOUT)
        self.add_workout_details(workout_details, document=document, section=workout_file)
        self.add_workout_to_document(interval, document=document, section=workout_section, parent_section=workout_file)
        document.appendChild(workout_file)
        return document
