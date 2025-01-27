import json
import logging
import sys
from http import HTTPStatus, client
from time import sleep

import requests

from exceptions import (
    ApiError,
    EndpointUrlMissing,
    ExpectedKeyNotFound,
    RequestError,
    UserListsDontMatch,
)

ENDPOINT_URL = "https://base.media108.ru/training/sample/"
WAIT_TIME = 1  # Sleep time between requests

METADATA_KEY = "metadata"
ACHIEVEMENTS_KEY = "achievements"
EXAMPLE_USER_DICT = {METADATA_KEY: dict, ACHIEVEMENTS_KEY: dict}

DUMP_RESULTS_TO_FILE = 0  # Set to 1 to export results to Json file
FILE_NAME = "results"


logger = logging.getLogger(__name__)
handler = logging.StreamHandler(stream=sys.stdout)
logger.addHandler(handler)


def log_function(func):
    """Logger decorator."""

    def wrapper(*args, **kwargs):
        logger_message = f"""Calling {func.__name__}
                       with args: {args},
                       kwargs: {kwargs}"""
        logger.debug(logger_message)
        result = func(*args, **kwargs)
        logger_message = f"{func.__name__} returned: {result}"
        logger.debug(logger_message)
        return result

    return wrapper


@log_function
def get_api_answer(endpoint):
    """
    Sends request to passed endpoint.
    Checks if endpoint is available and HTTPStatus is OK.
    Returns API answer as a dictionary.
    """
    logger_message = f"Requesting API response from {endpoint}..."
    logger.debug(logger_message)
    try:
        response = requests.get(endpoint)
        response_code = response.status_code
        logger_message = f"Response status code: {response_code}."
        logger.debug(logger_message)
        achievements_json = response.json()
    except requests.RequestException as error:
        logger.error(error, exc_info=True)
        raise RequestError(error)
    if response_code != HTTPStatus.OK:
        e = ApiError(response_code, client.responses[response_code])
        logger.error(e, exc_info=True)
        raise e
    return achievements_json


@log_function
def find_unique_achievements(dict_one, dict_two):
    """
    Generates 'unique_pairs' dict consisting of key: value
    pairs found only in dict_two.
    Returns 'unique_pairs' dict.
    """
    unique_pairs = {
        key: value for key, value in dict_two.items() if key not in dict_one
    }
    return unique_pairs


@log_function
def check_type(object_to_check, expected_type=dict):
    """Checks object type. Raises TypeError if
    type doesn't match the expected type."""
    if not isinstance(object_to_check, expected_type):
        reponse_type = type(object_to_check)
        e = TypeError(
            f"""Invalid object recieved.
                        {expected_type.__name__} expected, got
                        {reponse_type.__name__} instead."""
        )
        logger.error(e, exc_info=True)
        raise e


@log_function
def check_keys(dict_to_check, example=EXAMPLE_USER_DICT):
    """
    Checks if all the expected keys are present and
    belong to the expected object types.
    Pairs of expected keys and their types passed in the 'example'
    dict.
    """
    check_type(dict_to_check)
    for key, value in example.items():
        if key not in dict_to_check.keys():
            e = ExpectedKeyNotFound(key)
            logger.error(e, exc_info=True)
            raise e
        check_type(dict_to_check[key], value)


@log_function
def process_response(first_response, second_response):
    """
    Processes two response dicts:
        - Extracts users
        - For each user:
          - Checks if all keys are present and values
          are of expected type by calling check_keys()
          - Compares achievement dicts by calling
          find_unique_achievements()
          - Generates a dict with metadata and unique
          achievements and adds it to 'results' dict
        - Returns 'results' dict with.
    """
    results = {}
    for user, user_data in second_response.items():
        if user not in first_response.keys():
            error = UserListsDontMatch(user)
            logger.error(error, exc_info=True)
            raise error
        check_keys(user_data)
        check_keys(first_response[user])
        achievements_one = first_response[user][ACHIEVEMENTS_KEY]
        achievements_two = user_data[ACHIEVEMENTS_KEY]
        current_user = {
            METADATA_KEY: user_data[METADATA_KEY],
            ACHIEVEMENTS_KEY: find_unique_achievements(
                achievements_one, achievements_two
            ),
        }
        results[user] = current_user
    return results


def main():
    """Main logic."""
    if not ENDPOINT_URL:
        error = EndpointUrlMissing()
        logger.critical(error, exc_info=True)
        raise error
    first_response = get_api_answer(ENDPOINT_URL)
    sleep(WAIT_TIME)
    second_response = get_api_answer(ENDPOINT_URL)
    results = process_response(first_response, second_response)
    return results


if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)s, %(name)s, %(levelname)s, %(message)s",
        level=logging.INFO,
        filename="user_achievements_analyzer.log",
        filemode="a",
    )
    results = main()
    if DUMP_RESULTS_TO_FILE:
        json_file_path = f"{FILE_NAME}.json"
        with open(json_file_path, "w", encoding="utf8") as file:
            json.dump(results, file, indent=4, ensure_ascii=False)
            logger.info("Json dumped successfully!")
    else:
        print(results)
