from abc import ABC, abstractmethod
from pathlib import Path

from .models import JobListItem


class ExecuteCommandDriver(ABC):
    class PolicyError(Exception):
        def __init__(self, message: str):
            self.message = message
            super().__init__("<Execute Policy Error> ", self.message)

    def __init__(self):
        pass

    def submit_command(self, job: Path) -> str:
        return ["sh", job.script]

    @abstractmethod
    def policy_n_scripts_submission(self, n_from_cli: int) -> int:
        "Allow to conditionaly override the number of scripts to submit"

    @abstractmethod
    def policy_job_map(self, job: JobListItem) -> JobListItem:
        "Allow to conditionaly override the job to submit"

    @abstractmethod
    def policy_max_submissions(self) -> int:
        "Allow to clamp the number of submissions"

    @abstractmethod
    def policy_start_submission(
        self, no_date_jobs: list[JobListItem], with_date_jobs: list[JobListItem]
    ):
        "Allow to conditionaly stop the submission of jobs before it starts"


class DefaultExecuteCommandDriver(ExecuteCommandDriver):
    def policy_n_scripts_submission(self, n_from_cli: int) -> int:
        return n_from_cli

    def policy_job_map(self, job: JobListItem) -> JobListItem:
        return job

    def policy_start_submission(
        self, no_date_jobs: list[JobListItem], with_date_jobs: list[JobListItem]
    ):
        return

    def policy_max_submissions(self) -> int:
        "Allow to clamp the number of submissions"
        return -1
