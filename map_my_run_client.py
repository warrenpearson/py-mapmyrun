import json
import sys
from time import sleep

import requests


class MapMyRunClient:
    def __init__(self):
        self.base_url = (
            "https://www.mapmyrun.com/leaderboard/challenge_aPjjK4gDlw_overall/page/"
        )
        self.per_page = "/?per_page=50"
        self.search_distance = 100

    def find_by_distance(self, args):
        distance = float(args[1])
        future = True if len(args) > 2 else False
        found = False
        offset = 1
        # seen = list()

        if len(args) > 3:
            offset = int(args[2])
            self.search_distance = 20

        num_checks = 0

        while found is False:
            res = self.get_result(offset)
            num_checks += 1
            min_value, max_value = self.get_range(res)
            print(f"{offset}: {min_value} - {max_value} [{self.search_distance}]")

            if min_value < distance:
                if max_value > distance:
                    break
                offset = int(offset - self.search_distance)
                self.search_distance = int(self.search_distance / 2)

                if self.search_distance == 0:
                    self.search_distance = 1

            offset += self.search_distance
            sleep(0.1)

        print(f"{num_checks} requests")
        self.find_me(int(offset), future)

    def get_range(self, res):
        max_value = res["page"][0]["scores"]["distance"]["value"]
        min_value = res["page"][-1]["scores"]["distance"]["value"]
        return min_value, max_value

    def get_match(self, res, distance, offset):
        max_value = res["page"][0]["scores"]["distance"]["value"]
        min_value = res["page"][-1]["scores"]["distance"]["value"]
        print(f"{offset}: {min_value} / {max_value}")

        if max >= distance >= min:
            print("Yay, match")
            return True

        return False

    def get_max(self, res):
        person = res["page"].first
        return float(person["scores"]["distance"]["value"])

    def find_me(self, offset, future):
        found = False

        while found is False:
            res = self.get_result(offset)
            found = self.check(res)
            offset = str(int(offset) + 1)

            if future:
                break

            sleep(0.1)

    def get_result(self, offset):
        url = self.base_url + str(offset) + self.per_page
        print(url)

        response = requests.get(url, {"timeout": 5})  # , connecttimeout: 5)
        if response.status_code != 200:
            print(f"Got response #{response.status_code}, exiting")
            sys.exit()

        response = json.loads(response.text)
        return response["result"]

    def check(self, res):
        status = False
        for person in res["page"]:
            if person["display_name"] == "Warren Pearson":
                # print(json.dumps(person, indent=4))
                status = True
                break
        self.display(res)
        return status

    def display(self, res):
        total_count = f"Total count: {res['count']}"
        print(total_count)

        for person in res["page"]:
            me = ""
            if person["display_name"] == "Warren Pearson":
                me = "<<<<<"

            distance = person["scores"]["distance"]["value"]
            distance = round(float(distance), 2)
            workouts = person["scores"]["workouts"]["value"]
            wks = "workouts"
            if workouts == 1:
                wks = "workout"
            print(
                f"{person['rank']}. {person['display_name']}: {workouts} {wks}, {distance}km {me}"
            )
            if me != "":
                break


if __name__ == "__main__":
    MapMyRunClient().find_by_distance(sys.argv)
