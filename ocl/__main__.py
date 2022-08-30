import copy
import json
import logging
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Optional, Union

import requests
import typer
from appdirs import AppDirs
from iterfzf import iterfzf
from rich import print
from rich.progress import Progress, SpinnerColumn, TextColumn
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from .cluster import ClusterQueryData, ClusterV1, query_string

appdirs = AppDirs("ocl", "ca-net")


def get_var(var_name: str, default: Any = None) -> str:
    if cmd := os.getenv(f"OCL_{var_name}_COMMAND"):
        return (
            run(cmd, shell=True, check=True, capture_output=True)
            .stdout.decode("utf-8")
            .rstrip("\n")
        )
    if default is not None:
        return os.environ.get(f"OCL_{var_name}", default)
    return os.environ[f"OCL_{var_name}"]


def select_cluster(cluster_name: str = "") -> ClusterV1:
    clusters = clusters_from_app_interface()
    user_clusters = [
        ClusterV1(**c) for c in json.loads(get_var("USER_CLUSTERS", default="[]"))
    ]
    clusters_dict = {c.name: c for c in clusters + user_clusters}

    if not cluster_name:
        cluster_name = iterfzf((cname for cname in sorted(clusters_dict.keys())))
        if not cluster_name:
            sys.exit(0)
    return clusters_dict[cluster_name]


def clusters_from_app_interface() -> list[ClusterV1]:
    headers = {"Authorization": get_var("APP_INT_TOKEN")}
    res = requests.post(
        url=get_var("APP_INTERFACE_URL"),
        json={"query": query_string()},
        headers=headers,
    )
    res.raise_for_status()
    clusters = ClusterQueryData(**res.json()["data"]).clusters or []
    return [c for c in clusters if c.auth]


def auth_url(console_url: str) -> str:
    apps_suffix = ".".join(console_url.split(".")[1:])
    return f"https://oauth-openshift.{apps_suffix}/oauth/authorize?client_id=openshift-browser-client&idp=github-app-sre&redirect_uri=https%3A%2F%2Foauth-openshift.{apps_suffix}%2Foauth%2Ftoken%2Fdisplay&response_type=code"


def kubeconfig(cluster: ClusterV1) -> str:
    return f"{Path.home()}/.kube/config_{cluster.name}"


def run(
    cmd: Union[list[str], str],
    shell: bool = False,
    check: bool = True,
    capture_output: bool = True,
    cluster: Optional[ClusterV1] = None,
) -> subprocess.CompletedProcess:
    env = copy.deepcopy(os.environ)
    if cluster:
        env["KUBECONFIG"] = kubeconfig(cluster)
        env["OCL_CLUSTER_NAME"] = cluster.name
    return subprocess.run(
        cmd, shell=shell, check=check, env=env, capture_output=capture_output
    )


def oc_login(cluster: ClusterV1, token: str) -> None:
    run(
        ["oc", "login", f"--token={token}", f"--server={cluster.server_url}"],
        cluster=cluster,
    )


def oc_project(cluster: ClusterV1, project: str) -> None:
    run(["oc", "project", project], cluster=cluster)


def oc_whoami(cluster: ClusterV1) -> None:
    run(["oc", "whoami"], cluster=cluster)


def setup_driver(user_data_dir_path: Path, debug: bool) -> WebDriver:
    chrome_options = Options()
    if not debug:
        chrome_options.add_argument("--headless")
    chrome_options.add_argument(f"user-data-dir={user_data_dir_path}")
    driver = webdriver.Chrome(options=chrome_options)
    driver.implicitly_wait(int(get_var("WAIT", default=2)))
    return driver


def github_login(driver: WebDriver) -> None:
    login_el = driver.find_element(By.ID, "login_field")
    login_el.send_keys(get_var("GITHUB_USERNAME"))
    pass_el = driver.find_element(By.ID, "password")
    pass_el.send_keys(get_var("GITHUB_PASSWORD"))
    # submit form
    driver.find_element(By.CSS_SELECTOR, ".btn-primary").click()
    # Filling the OTP token - form is auto submitted
    otp_el = driver.find_element(By.ID, "totp")
    otp_el.send_keys(get_var("GITHUB_TOTP"))


def oc_setup(cluster: ClusterV1, driver: WebDriver) -> None:
    with Progress(
        SpinnerColumn(), TextColumn("[progress.description]{task.description}")
    ) as progress:
        task = progress.add_task(description="Testing already logged in ..", total=1)
        try:
            oc_whoami(cluster)
            progress.remove_task(task)
        except subprocess.CalledProcessError:
            # not logged in
            progress.remove_task(task)

            try:
                task = progress.add_task(description="Retrieving token ...", total=1)
                driver.get(auth_url(cluster.console_url))

                if driver.current_url.startswith("https://github.com/login?"):
                    subtask = progress.add_task(
                        description="GitHub  login ...", total=1
                    )
                    github_login(driver=driver)
                    progress.remove_task(subtask)
                    if driver.current_url.startswith(
                        "https://github.com/login/oauth/authorize?"
                    ):
                        # grant access
                        subtask = progress.add_task(
                            description="GitHub  authorize app-sre ...", total=1
                        )
                        time.sleep(4)
                        driver.find_element(By.ID, "js-oauth-authorize-btn").click()
                        progress.remove_task(subtask)

                # Clicking the "Display Token" button
                driver.find_element(By.CSS_SELECTOR, "button").click()
                # Getting the auth token
                token = driver.find_element(By.CSS_SELECTOR, "code").text
                progress.remove_task(task)
            finally:
                for handle in driver.window_handles:
                    driver.switch_to.window(handle)
                    driver.close()

            task = progress.add_task(description="CLI login ...", total=1)
            oc_login(cluster=cluster, token=token)
            progress.remove_task(task)


def main(
    cluster_name: str = typer.Argument(None, help="Cluster name"),
    project: str = typer.Argument(None, help="Namespace/Project"),
    debug: bool = False,
    open_in_browser: bool = False,
):
    logging.basicConfig(
        level=logging.INFO if not debug else logging.DEBUG, format="%(message)s"
    )

    cluster = select_cluster(cluster_name)
    if open_in_browser:
        subprocess.run(["open", cluster.console_url])
        sys.exit(0)

    driver = setup_driver(user_data_dir_path=Path(appdirs.user_cache_dir), debug=debug)
    try:
        oc_setup(cluster, driver)
    except subprocess.CalledProcessError as e:
        print(f"[bold red]'oc login' failed![/]\nException: {e}")
        sys.exit(1)

    if project:
        try:
            oc_project(cluster=cluster, project=project)
        except subprocess.CalledProcessError:
            print(
                f"[bold red]Entering {project} failed! Maybe this project doesn't exist or you don't have proper permissions.[/]"
            )
            project = ""

    print(
        f"Spawn new shell for [bold green] {cluster.name}[/]{f'[bold yellow]/{project}[/]' if project else ''} ({cluster.console_url}). Use exit or CTRL+d to leave it ..."
    )
    run(os.environ["SHELL"], check=False, cluster=cluster, capture_output=False)
    print(
        "Thank you for using openshift-login. :man_bowing: Have a great day ahead! :red_heart-emoji:"
    )


def typer_run():
    typer.run(main)


if __name__ == "__main__":
    typer_run()
