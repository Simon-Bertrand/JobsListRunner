import argparse
from datetime import datetime
from pathlib import Path
import sys
import yaml
import subprocess


from .drivers import DefaultExecuteCommandDriver, ExecuteCommandDriver

from .io import load_jobs, save_jobs

from .models import JobListItem


class JobListArgumentValidation:
    def __init__(self, args):
        self.jobs_list = Path(args.jobs_list)
        if not self.jobs_list.exists():
            raise ValueError(f"File {self.jobs_list} does not exist")
        with open(self.jobs_list) as f:
            self.jobs = yaml.safe_load(f)


class Cli:
    DEFAULT_JOB_LIST_PATH = Path("./jobs_list.yaml")
    DEFAULT_SCRIPT_EXTENSION = ".sh"

    class ClearCommand(JobListArgumentValidation):
        def __init__(self, args):
            super().__init__(args)

        def run(self):
            no_date_jobs, with_date_jobs = load_jobs(self.jobs_list)
            for job in with_date_jobs:
                job.date = None
            save_jobs(no_date_jobs + with_date_jobs, self.jobs_list)

    class GenerateCommand:
        def __init__(self, args):
            self.scripts_dir = Path(args.scripts_dir)
            self.scripts = list(
                self.scripts_dir.glob("**/*" + Cli.DEFAULT_SCRIPT_EXTENSION)
            )
            if len(self.scripts) == 0:
                raise ValueError(
                    f"No scripts terminating by {Cli.DEFAULT_SCRIPT_EXTENSION} found in {self.scripts_dir}"
                )

            self.out = args.out or Cli.DEFAULT_JOB_LIST_PATH
            if self.out.exists():
                raise ValueError(
                    f"File {self.out} already exists. Remove it first or choose another path"
                )

        def run(self):
            with open(self.out, "w") as f:
                yaml.dump(
                    [
                        JobListItem(script=script).model_dump()
                        for script in self.scripts
                    ],
                    f,
                )

    class ExecuteCommand(JobListArgumentValidation):
        def __init__(
            self, args, driver: ExecuteCommandDriver = DefaultExecuteCommandDriver()
        ):
            self.n = int(args.n)
            super().__init__(args)
            self.driver = driver

        def run(self):
            failed_tag = False
            n = max(
                0,
                min(
                    int(self.driver.policy_max_submissions()),
                    int(self.driver.policy_n_scripts_submission(self.n)),
                ),
            )
            ith_job = None
            no_date_jobs, with_date_jobs = load_jobs(self.jobs_list)
            self.driver.policy_start_submission(no_date_jobs, with_date_jobs)
            for ith_job, job in enumerate(no_date_jobs[:n]):
                job = self.driver.policy_job_map(job)
                assert isinstance(job, JobListItem), (
                    "Driver policy_job_map must return a JobListItem"
                )
                print(100 * "_")
                print(f"-> Executing : {job.script}")
                result = subprocess.run(
                    self.driver.submit_command(job), capture_output=True, text=True
                )
                if result.returncode == 0:
                    print("Command executed successfully. Output : ")
                    print(
                        "    \033[90m>>"
                        + result.stdout.replace("\n", "\n    >>")[:-2].strip()
                        + "\033[0m"
                    )
                    job.date = datetime.now()

                else:
                    print(
                        f"Command failed with exit code {result.returncode}: {result.stderr}"
                    )
                    failed_tag = True
                print(100 * "_")
            if ith_job is None:
                print("No job to execute")

            else:
                print(f"Executed {ith_job + 1} jobs (queried : {self.n})")
                save_jobs(no_date_jobs + with_date_jobs, self.jobs_list)
                if failed_tag:
                    sys.exit(1)
                sys.exit(0)

    def __init__(
        self, execute_driver: ExecuteCommandDriver = DefaultExecuteCommandDriver()
    ):
        parser = argparse.ArgumentParser()
        subcommands = parser.add_subparsers(dest="command", required=True)
        sub_generate = subcommands.add_parser("generate")
        sub_execute = subcommands.add_parser("execute")
        sub_clear = subcommands.add_parser("clear")

        sub_generate.add_argument("scripts_dir", help="Scripts folder path", type=str)
        sub_generate.add_argument(
            "-o", "--out", help="Path to jobs list yaml file", type=str
        )
        sub_clear.add_argument("jobs_list", help="Path to job list", type=str)

        sub_execute.add_argument("jobs_list", help="Path to job list", type=str)
        sub_execute.add_argument(
            "-n", help="Number of scripts to execute", type=int, default=1
        )

        self.args = parser.parse_args()
        assert isinstance(execute_driver, ExecuteCommandDriver), (
            "execute_driver must be a ExecuteCommandDriver"
        )
        match self.args.command:
            case "generate":
                self.command = self.GenerateCommand(self.args)
            case "execute":
                self.command = self.ExecuteCommand(self.args, driver=execute_driver)
            case "clear":
                self.command = self.ClearCommand(self.args)
            case _:
                raise ValueError(f"Unknown command {self.args.command}")
        try:
            self.command.run()
        except ExecuteCommandDriver.PolicyError as e:
            print(f"{e.args[0]} {e.message}")
            sys.exit(1)


def main():
    Cli()


if __name__ == "__main__":
    main()
