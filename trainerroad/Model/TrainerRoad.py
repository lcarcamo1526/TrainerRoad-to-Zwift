import asyncio
import datetime as dt
import http
import json
import logging
from http import HTTPStatus
from io import StringIO

import aiohttp
import pandas as pd
import requests
from aiohttp import BasicAuth
from lxml import etree
from random_user_agent.params import SoftwareName, OperatingSystem
from random_user_agent.user_agent import UserAgent

from trainerroad.Utils.Str import USERNAME, PASSWORD
from trainerroad.Utils.Warning import *

logger = logging.getLogger(__name__)


class TrainerRoad:
    _ftp = 'Ftp'
    _weight = 'Weight'
    _units_metric = 'kmh'
    _login_name = 'LoginName'
    _date = "Date"
    _activity_id = "Activity.Id"
    _activity_workout_name = "Name"

    _units_imperial = 'mph'
    _input_data_names = (_ftp, _weight, 'Marketing')
    _select_data_names = ('TimeZoneId', 'IsMale', 'IsPrivate',
                          'Units', 'IsVirtualPowerEnabled', 'TimeZoneId')
    _numerical_verify = (_ftp, _weight)
    _string_verify = _select_data_names + ('Marketing',)
    _login_url = 'https://www.trainerroad.com/app/login'
    _logout_url = 'https://www.trainerroad.com/app/logout'
    _member_info = "https://www.trainerroad.com/app/api/member-info"
    _rider_url = 'https://www.trainerroad.com/app/profile/rider-information'
    _download_tcx_url = 'http://www.trainerroad.com/cycling/rides/download'
    _workouts_url = 'https://api.trainerroad.com/api/careerworkouts'
    _calendar_url = "https://www.trainerroad.com/app/api/calendar/activities/"
    _workout_details = "https://www.trainerroad.com/app/api/workoutdetails/{}"

    # TODO move endpoints into singleton class
    _rvt = '__RequestVerificationToken'

    def __init__(self, username, password):
        self._username = username
        self._password = password
        self._session = None
        self.logger = logging.getLogger('')
        self.connect()
        self._display_name = self.login_name

    def connect(self):
        self._session = requests.Session()
        self._session.auth = (self._username, self._password)

        data = {USERNAME: self._username,
                PASSWORD: self._password}

        r = self._session.post(self._login_url, data=data,
                               allow_redirects=False)
        headers = r.headers
        software_names = [SoftwareName.CHROME.value, SoftwareName.FIREFOX.value]
        operating_systems = [OperatingSystem.MAC_OS_X, OperatingSystem.WINDOWS.value]
        user_agent_rotator = UserAgent(software_names=software_names, operating_systems=operating_systems, limit=100)
        user_agent = user_agent_rotator.get_random_user_agent()
        self.logger.warning(f"Current User Agent: {user_agent}")
        headers["User-Agent"] = user_agent
        r.headers = headers

        if (r.status_code != http.HTTPStatus.OK) and (r.status_code != http.HTTPStatus.FOUND):
            # There was an error
            # todo move warning into singleton class
            raise RuntimeError("Error logging in to TrainerRoad (Code {})"
                               .format(r.status_code))

        logger.warning(WARNING_LOGGING_AS.format(self._username))

    def disconnect(self):
        r = self._session.get(self._logout_url, allow_redirects=False)
        if (r.status_code != http.HTTPStatus.OK) and (r.status_code != http.HTTPStatus.FOUND):
            raise RuntimeError("Error logging out of TrainerRoad (Code {})"
                               .format(r.status_code))

        self._session = None
        logger.info('Logged out of TrainerRoad as "{}"'.format(self._username))

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.disconnect()

    def _parse_value(self, tree, name):
        rtn = tree.xpath('//form//input[@name="{}"]/@value'.format(name))
        if not rtn:
            raise RuntimeError('Input {} not found in form'.format(name))

        return rtn[0]

    def _parse_name(self, tree, name):
        rtn = tree.xpath('//form//select[@name="{}"]//option'
                         '[@selected="selected"]/@value'.format(name))
        if not rtn:
            raise RuntimeError('Input {} not found in form'.format(name))

        return rtn[0]

    def _get(self, url):
        if self._session is None:
            raise RuntimeError('Not Connected')

        r = self._session.get(url)

        if r.status_code != http.HTTPStatus.OK:
            raise RuntimeError("Error getting info from TrainerRoad (Code {})"
                               .format(r.status_code))

        return r

    def _post(self, url, data):
        if self._session is None:
            raise RuntimeError('Not Connected')

        r = self._session.post(url, data)

        if r.status_code != 200:
            raise RuntimeError("Error posting info to TrainerRoad (Code {})"
                               .format(r.status_code))

        return r

    def _read_member_info(self):
        response: requests.Response = self._session.get(self._member_info)
        if response.status_code == HTTPStatus.OK:
            return response.json()
        else:
            self.logger.warning('Failed to get member info')
            self.logger.warning(f"ERROR: {response.text} status_code: {response.status_code}")
            self.logger.warning(f"ERROR: {response.json()}")
            raise RuntimeError('Failed to get member info')

    def _read_profile(self):
        r = self._get(self._rider_url)
        parser = etree.HTMLParser()
        tree = etree.parse(StringIO(r.text), parser)

        token = self._parse_value(tree, self._rvt)

        input_data = {}
        for key in self._input_data_names:
            input_data[key] = self._parse_value(tree, key)

        select_data = {}
        for key in self._select_data_names:
            select_data[key] = self._parse_name(tree, key)

        return dict(**input_data, **select_data), token

    def _write_profile(self, new_values):
        # Read values
        data, token = self._read_profile()

        logger.info("Read profile values {}".format(data))
        logger.debug("Token = {}".format(token))

        # Update values with new_values
        for key, value in new_values.items():
            if key not in data:
                raise ValueError("Key \"{}\" is not in profile form"
                                 .format(key))
            data[key] = str(value)

        logger.info("New profile values {}".format(data))

        # Now post the form
        token = {self._rvt: token}
        self._post(self._rider_url, data=dict(**data, **token))

        # Now re-read to check
        _data, token = self._read_profile()

        logger.info("Read profile values (verification) {}".format(_data))

        for key in self._numerical_verify:
            logger.debug('Numerically verifying key "{}" "{}" with "{}"'
                         .format(key, data[key], _data[key]))
            if float(data[key]) != float(_data[key]):
                raise RuntimeError('Failed to verify numerical key {}'
                                   .format(key))
        for key in self._string_verify:
            logger.debug('String verifying key "{}" "{}" with "{}"'
                         .format(key, data[key], _data[key]))
            if data[key] != _data[key]:
                raise RuntimeError('Failed to verify string key {}'.format(key))

        return

    @property
    def ftp(self) -> int:
        values, token = self._read_profile()
        return values[self._ftp]

    @ftp.setter
    def ftp(self, value):
        self._write_profile({self._ftp: value})

    # def loginName(self):

    @property
    def weight(self) -> int:
        values, token = self._read_profile()
        return values[self._weight]

    @property
    def login_name(self) -> str:
        r = self._read_member_info()
        if bool(r):
            login_name: str = r.get(self._login_name)
            if bool(login_name):
                return login_name.lower()
        return ''

    @weight.setter
    def weight(self, value):
        self._write_profile({self._weight: value})

    def download_tcx(self, id):
        res = self._session.get('{}/{}'.format(self._download_tcx_url, str(id)))
        if res.status_code != 200:
            raise RuntimeError("Unable to download (code = {})"
                               .format(res.status_code))

        return res.text

    def get_workouts(self):
        res = self._session.get(self._workouts_url)
        if res.status_code != 200:
            raise RuntimeError("Unable to download (code = {})"
                               .format(res.status_code))

        data = json.loads(res.text)
        logger.debug(json.dumps(data, indent=4, sort_keys=True))

        logger.info('Received info on {} workouts'.format(len(data)))

        return data

    def get_workout(self, guid):
        res = self._session.get(self._workout_url
                                + '?guid={}'.format(str(guid)))

        if res.status_code != 200:
            raise RuntimeError('Unable to get workout "{}" (Code = {})'
                               .format(guid, res.status_code))

        data = json.loads(res.text)
        logger.debug(json.dumps(data, indent=4, sort_keys=True))

        return data

    def get_training_plans(self, start_date, end_date) -> pd.DataFrame:
        """

        :param start_date: date must be formatted as month/day/year
        :param end_date: date must be formatted as month/day/year
        :return:
        """
        params = f'{self._display_name}?startDate={start_date}&endDate={end_date}'
        endpoint = self._calendar_url + params
        today = dt.datetime.now().strftime("%Y-%m-%d")

        response = self._session.get(endpoint)
        if response.status_code == HTTPStatus.OK:
            calendar: dict = response.json()
            calendar_df = pd.json_normalize(calendar)[[self._date, self._activity_workout_name, self._activity_id]]
            calendar_df.dropna(inplace=True)
            calendar_df[self._activity_id] = calendar_df[self._activity_id].astype(int)
            calendar_df[self._date] = pd.to_datetime(calendar_df[self._date])
            calendar_df = calendar_df.loc[calendar_df[self._date] >= today]
            calendar_df.sort_values(self._date, ascending=True, inplace=True, ignore_index=True)
            return calendar_df

        else:
            self.logger.warning(params)
            self.logger.warning(response.text)
            raise RuntimeError('Unable to get training plan: (Code = {})'
                               .format(response.status_code))

    async def _get_workout_detail(self, session, workout_id: str):
        url = self._workout_details.format(workout_id)
        async with session.get(url) as resp:
            response = await resp.json()
            return response

    async def get_workouts_details(self, workouts) -> tuple:
        tasks = []
        async with aiohttp.ClientSession(auth=BasicAuth(login=self._username, password=self._password)) as session:
            data = {USERNAME: self._username,
                    PASSWORD: self._password}
            async with session.post(self._login_url, data=data) as response:
                if response.status == HTTPStatus.OK:
                    logger.warning(WARNING_LOGGING_AS.format(self._username))

                    for workout in workouts:
                        tasks.append(asyncio.ensure_future(self._get_workout_detail(session, workout_id=workout)))

                    output = await asyncio.gather(*tasks)
                    return output

                else:
                    raise RuntimeError("Error logging in to TrainerRoad (Code {})"
                                       .format(response.status))
