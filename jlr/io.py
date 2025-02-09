from datetime import datetime
from pathlib import Path
import yaml

from .models import JobListItem


def load_jobs(jobs_list_path: Path) -> tuple[list[JobListItem], list[JobListItem]]:
    no_date_jobs = []
    with_date_jobs = []
    with open(jobs_list_path) as f:
        data = yaml.safe_load(f)
        if data is None:
            raise ValueError(f"File {jobs_list_path} is wrongly configured")
        for el in data:
            (with_date_jobs if el["date"] is not None else no_date_jobs).append(
                JobListItem(**el)
            )
    return no_date_jobs, with_date_jobs


def save_jobs(jobs: list[JobListItem], jobs_list_path: Path):
    with open(jobs_list_path, "w") as f:
        yaml.dump(
            [
                job.model_dump()
                for job in sorted(
                    jobs,
                    key=lambda x: x.date or datetime.min,
                    reverse=True,
                )
            ],
            f,
        )
