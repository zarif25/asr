import datetime
import json
import os
from typing import Any, Dict, List
from models.activity import Activity
from models.task import Task
from models.task_list import TaskList

DATE_FORMAT = "%Y-%m-%d"
DB_DIR = "/home/seven89/Documents/asr-db"


class Journal:
    def __init__(self, activities: List[Activity], date: datetime.date) -> None:
        self.date = date
        self.activities = activities
        self.filepath = os.path.join(
            DB_DIR, "journal", str(date.year), str(date.month), f"{date.day}.json"
        )

    @property
    def to_py_obj(self):
        return {
            "date": self.date.strftime(DATE_FORMAT),
            "activities": [a.to_py_obj for a in self.activities],
        }

    @classmethod
    def from_py_obj(cls, data: Dict[str, Any]):
        data["activities"] = [Activity.from_py_obj(d) for d in data["activities"]]
        data["date"] = datetime.datetime.strptime(data["date"], DATE_FORMAT)
        return cls(**data)

    @classmethod
    def create_month_dir_if_does_not_exist(self, date: datetime.date):
        month_dir = os.path.join(DB_DIR, "journal", str(date.year), str(date.month))
        if not os.path.exists(month_dir):
            os.makedirs(month_dir)

    @classmethod
    def load(cls, date: datetime.date = datetime.datetime.now()):
        filepath = os.path.join(
            DB_DIR, "journal", str(date.year), str(date.month), f"{date.day}.json"
        )
        cls.create_month_dir_if_does_not_exist(date)
        if not os.path.exists(filepath):
            with open(filepath, "w") as file:
                json.dump({"date": date.strftime(DATE_FORMAT), "activities": []}, file)
        with open(filepath, "r") as file:
            data = json.load(file)
        return cls.from_py_obj(data)

    def save(self):
        self.create_month_dir_if_does_not_exist(self.date)
        with open(self.filepath, "w") as file:
            json.dump(self.to_py_obj, file)

    def start_task(self, task_path: str):
        now = datetime.datetime.now()
        activity = Activity(name=task_path, start=now.time())
        task_list = TaskList.load()
        task_list.start_task(task_path, now)
        self.activities.append(activity)
        self.save()

    def stop_task(self):
        if self.activities[-1].end == None:
            now = datetime.datetime.now()
            task_list = TaskList.load()
            task_path = self.activities[-1].name
            task_list.stop_task(task_path, now)
            self.activities[-1].end = now.time()
            self.save()
        else:
            raise Exception  # TODO: better way to handle this
