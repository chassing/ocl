import copy
import json
import logging
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any
from typing import Optional
from typing import Tuple
from typing import Union

import requests
import typer
from appdirs import AppDirs
from diskcache import Cache
from flufl.lock import Lock
from iterfzf import iterfzf
from rich import print
from rich.progress import Progress
from rich.progress import SpinnerColumn
from rich.progress import TextColumn
from rich.text import Text
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from .cluster import ClusterQueryData
from .cluster import ClusterV1
from .cluster import query_string

appdirs = AppDirs("ocl", "ca-net")
lock_file_name = Path(tempfile.gettempdir()) / "ocl.lock"
lock = Lock(str(lock_file_name), lifetime=60, default_timeout=65)
cache = Cache(directory=str(Path(appdirs.user_cache_dir) / "gql_cache"))

ONE_WEEK = 7 * 24 * 60 * 60
BANNER = """
            ';cloooolc;'            ';clloooolc;'        ':lll:'
          ;d0NWMMMMMMWN0d;        ;d0NWMMMMMMMWN0d;      oNMMMXc
         cKMMMMMMMMMMMMMMKl      cKWMMMMMMMMMMMMMWKl     oNMMMXl
        ;0MMMMXkllloONMMMMXc    ;0MMMMX0klclokNMMMMXc    oNMMMNl
        dWMMMNo      dNMMMWx'   oNMMMNo'      oNMMMWx'   oWMMMNl
       'kMMMM0;      ;KMMMMO,  'kMMMM0;       'ldddd:    dWMMMNl
       ,OMMMMO,      ,0MMMM0;  ,OMMMMO,                  dWMMMXc
       ;0MMMMO,      ,OMMMM0;  ;0MMMMO,                  dWMMMK:
       ,0MMMMk'      ,0MMMM0;  ,OMMMMO,                  dWMMMXc
       ,OMMMMO,      ;0MMMM0;  ,OMMMMO,        ';;;;'    dWMMMXc
       'kMMMMK;      :KMMMMO,  'xWMMMK:       ;ONNNNx'   dWMMMK:
        oNMMMNx'    ,kWMMMWx    lNMMMWx:,    ,kWMMMWx'   dWMMMKc
        ,OWMMMWKkxxOKWMMMW0:    ,kWMMMWNKkxxOKWMMMW0:    dWMMMWX000000o'
         ;kWMMMMMMMMMMMMWk;      ;kNMMMMMMMMMMMMMNO;     xWMMMMMMMMMMMO,
          'cx0XNNWWWNX0xc'        'cx0XNNNNWWNX0xc'      oKXKKKXXKKKKKd'
             ;cloooolc;              ;clloooolc;         oKXKKKXXKKKKKd'
"""

app = typer.Typer(rich_markup_mode="rich")


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


def gql_query() -> dict[Any, Any]:
    if "gql_data" not in cache:
        headers = {"Authorization": get_var("APP_INT_TOKEN")}
        res = requests.post(
            url=get_var("APP_INTERFACE_URL"),
            json={"query": query_string()},
            headers=headers,
        )
        res.raise_for_status()
        cache.set("gql_data", res.json()["data"], expire=ONE_WEEK)
    return cache["gql_data"]


def clusters_from_app_interface() -> list[ClusterV1]:
    clusters = ClusterQueryData(**gql_query()).clusters or []
    return [c for c in clusters if c.auth]


def auth_url(console_url: str) -> str:
    apps_suffix = ".".join(console_url.split(".")[1:])
    return f"https://oauth-openshift.{apps_suffix}/oauth/authorize?client_id=openshift-browser-client&idp=github-app-sre&redirect_uri=https%3A%2F%2Foauth-openshift.{apps_suffix}%2Foauth%2Ftoken%2Fdisplay&response_type=code"


def kubeconfig(cluster: ClusterV1, temp_kube_config: bool) -> str:
    kc = f"{Path.home()}/.kube/config_{cluster.name}"
    if temp_kube_config:
        _, temp_file = tempfile.mkstemp(prefix=f"ocl.{cluster.name}.")
        shutil.copyfile(kc, temp_file)
        return temp_file
    return kc


def run(
    cmd: Union[list[str], str],
    shell: bool = False,
    check: bool = True,
    capture_output: bool = True,
    cluster: Optional[ClusterV1] = None,
    temp_kube_config: bool = False,
) -> subprocess.CompletedProcess:
    env = copy.deepcopy(os.environ)
    if cluster:
        env["KUBECONFIG"] = kubeconfig(cluster, temp_kube_config=temp_kube_config)
        env["OCL_CLUSTER_NAME"] = cluster.name
        env["OCL_CLUSTER_CONSOLE"] = cluster.console_url
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


def oc_check_login(cluster: ClusterV1) -> bool:
    try:
        run(["oc", "cluster-info"], cluster=cluster)
        return True
    except subprocess.CalledProcessError:
        return False


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


def oc_setup(cluster: ClusterV1, debug: bool, refresh_login: bool) -> None:
    with Progress(
        SpinnerColumn(), TextColumn("[progress.description]{task.description}")
    ) as progress:
        task = progress.add_task(description="Acquiring lock ...", total=1)
        with lock:
            progress.remove_task(task)

            if not refresh_login:
                task = progress.add_task(
                    description="Testing already logged in ..", total=1
                )
                logged_in = oc_check_login(cluster)
                progress.remove_task(task)

            if not refresh_login and logged_in:
                return

            # not logged in or login enforced
            task = progress.add_task(
                description="Opening browser headless ...", total=1
            )
            driver = setup_driver(
                user_data_dir_path=Path(appdirs.user_cache_dir), debug=debug
            )
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


def blend_text(
    message: str, color1: Tuple[int, int, int], color2: Tuple[int, int, int]
) -> Text:
    """Blend text from one color to another."""
    text = Text(message)
    r1, g1, b1 = color1
    r2, g2, b2 = color2
    dr = r2 - r1
    dg = g2 - g1
    db = b2 - b1
    size = len(text)
    for index in range(size):
        blend = index / size
        color = f"#{int(r1 + dr * blend):2X}{int(g1 + dg * blend):2X}{int(b1 + db * blend):2X}"
        text.stylize(color, index, index + 1)
    return text


def bye():
    print(
        "Thank you for using openshift-login. :man_bowing: Have a great day ahead! :red_heart-emoji:"
    )


@app.command(epilog="Made with :heart: by [blue]https://github.com/chassing[/]")
def main(
    cluster_name: str = typer.Argument(None, help="Cluster name"),
    project: str = typer.Argument(None, help="Namespace/Project"),
    debug: bool = typer.Option(False, help="Enable debug mode"),
    open_in_browser: bool = typer.Option(
        False, help="Open the console in browser instead of local shell"
    ),
    display_banner: bool = typer.Option(True, help="Display shiny OCL banner"),
    refresh_login: bool = typer.Option(
        False, help="Enforce a new login to refresh the session."
    ),
):
    logging.basicConfig(
        level=logging.INFO if not debug else logging.DEBUG, format="%(message)s"
    )
    if display_banner:
        print(blend_text(BANNER, (32, 32, 255), (255, 32, 255)))

    if open_in_browser and cluster_name == ".":
        cluster_name = os.environ.get("OCL_CLUSTER_NAME", "")
        if not cluster_name:
            print("[bold red]environment variable OCL_CLUSTER_NAME not set")
            sys.exit(1)
        project = run(["oc", "project", "-q"]).stdout.decode("utf-8").strip()

    cluster = select_cluster(cluster_name)
    browser_url = cluster.console_url

    if project:
        browser_url += f"/k8s/cluster/projects/{project}"

    if open_in_browser:
        print(f"[bold green]Opening [/] {browser_url}")
        subprocess.run(["open", browser_url])
        bye()
        sys.exit(0)

    try:
        oc_setup(cluster, debug=debug, refresh_login=refresh_login)
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
        f"""Spawn new shell, use exit or CTRL+d to leave it!

    URL: {browser_url}
    Cluster: [bold green] {cluster.name}[/]
    {f'Project: [bold yellow]☸ {project}[/]' if project else ''}"""
    )
    run(
        os.environ["SHELL"],
        check=False,
        cluster=cluster,
        capture_output=False,
        temp_kube_config=True,
    )
    bye()


if __name__ == "__main__":
    app()
