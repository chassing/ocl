import copy
import hashlib
import json
import logging
import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import webbrowser
from collections.abc import Generator
from pathlib import Path
from typing import Any

import requests
import typer
from appdirs import AppDirs
from diskcache import Cache
from flufl.lock import Lock
from iterfzf import iterfzf
from pyquery import PyQuery as pq  # noqa: N813
from requests_kerberos import (
    OPTIONAL,
    HTTPKerberosAuth,
)
from rich import print as rich_print
from rich.progress import (
    Progress,
    SpinnerColumn,
    TextColumn,
)
from rich.prompt import Prompt
from rich.text import Text

from openshift_cluster_login.gql_definitions.clusters import query as clusters_query
from openshift_cluster_login.gql_definitions.fragments.cluster import Cluster
from openshift_cluster_login.gql_definitions.namespaces import NamespaceV1
from openshift_cluster_login.gql_definitions.namespaces import (
    query as namespaces_query,
)

appdirs = AppDirs("ocl", "ca-net")
lock_file_name = Path(tempfile.gettempdir()) / "ocl.lock"
lock = Lock(str(lock_file_name), lifetime=60, default_timeout=65)
cache = Cache(directory=str(Path(appdirs.user_cache_dir) / "gql_cache"))

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


def get_var(var_name: str, default: Any = None, *, hidden: bool = False) -> str:
    env_var = f"OCL_{var_name}"
    if cmd := os.getenv(f"{env_var}_COMMAND"):
        return (
            run(cmd, shell=True, check=True, capture_output=True)
            .stdout.decode("utf-8")
            .rstrip("\n")
        )
    if default is not None:
        return os.environ.get(env_var, default)

    if env_var in os.environ:
        return os.environ[env_var]

    print(
        f"[bold red]Missing environment variable [bold green]{env_var}[bold green][/bold red]",
        quiet=False,
    )
    return Prompt.ask(f"Enter OCL_{var_name}", password=hidden)


def select_cluster(cluster_name: str) -> Cluster:
    clusters = clusters_from_app_interface()
    # user defined clusters
    clusters += [
        Cluster(**c) for c in json.loads(get_var("USER_CLUSTERS", default="[]"))
    ]
    clusters_dict = {c.name: c for c in clusters}
    if cluster_name not in clusters_dict:
        print(
            f"[bold red]Cluster [bold green]{cluster_name}[/bold green] not found. Available clusters:[/bold red]",
            quiet=False,
        )
        for cname in sorted(clusters_dict.keys()):
            print(f"  [bold green]{cname}[/]", quiet=False)
        sys.exit(1)
    return clusters_dict[cluster_name]


def select_namespace() -> NamespaceV1:
    namespaces_dict = {
        (ns.name, ns.cluster.name): ns for ns in namespaces_from_app_interface()
    }
    items = [f"{k[0]:<40} {k[1]}" for k in sorted(namespaces_dict.keys())]
    selected_item = iterfzf(items, __extra__=[f"--header={'Namespace':<40} Cluster"])
    if not selected_item:
        sys.exit(0)
    ns, cluster = re.split(r"\s+", selected_item)
    return namespaces_dict[ns.strip(), cluster.strip()]


def generate_checksum(input_string: str) -> str:
    return hashlib.sha256(input_string.encode("utf-8")).hexdigest()


def gql_query(query: str) -> dict[Any, Any]:
    checksum = generate_checksum(query)
    if checksum not in cache:
        headers = {}
        if token := get_var("APP_INT_TOKEN", hidden=True, default=""):
            headers["Authorization"] = token
        res = requests.post(
            url=get_var("APP_INTERFACE_URL"),
            json={"query": query},
            headers=headers,
            timeout=10,
        )
        res.raise_for_status()
        cache.set(
            checksum,
            res.json()["data"],
            expire=get_var("CACHE_TIMEOUT_MINUTES", default=60) * 60,
        )
    return cache[checksum]


def clusters_from_app_interface() -> list[Cluster]:
    clusters = clusters_query(query_func=gql_query).clusters or []
    return [c for c in clusters if c.auth]


def namespaces_from_app_interface() -> list[NamespaceV1]:
    return [
        ns
        for ns in namespaces_query(query_func=gql_query).namespaces or []
        if not ns.delete
    ]


def cluster_oauth(console_url: str, *, hypershift: bool) -> str:
    if hypershift:
        apps_suffix = ".".join(console_url.split(".")[3:])
        return f"oauth.{apps_suffix}"
    apps_suffix = ".".join(console_url.split(".")[1:])
    return f"oauth-openshift.{apps_suffix}"


def token_request_url(console_url: str, idp: str | None, *, hypershift: bool) -> str:
    url = cluster_oauth(console_url, hypershift=hypershift)
    if hypershift:
        return f"https://{url}/oauth/token/request"
    if idp:
        return f"https://{url}/oauth/authorize?client_id=openshift-browser-client&idp={idp}&redirect_uri=https%3A%2F%2F{url}%2Foauth%2Ftoken%2Fdisplay&response_type=code"
    raise ValueError("idp or hypershift must be set")


def token_display_url(console_url: str, *, hypershift: bool) -> str:
    url = cluster_oauth(console_url, hypershift=hypershift)
    return f"https://{url}/oauth/token/display"


def select_idp(console_url: str, idps: list[str]) -> str | None:
    for idp in idps:
        req = requests.get(
            token_request_url(console_url, idp, hypershift=False),
            allow_redirects=False,
            timeout=10,
        )
        try:
            req.raise_for_status()
            return idp
        except requests.exceptions.HTTPError:
            pass
    return None


def kubeconfig(cluster: Cluster, *, temp_kube_config: bool) -> str:
    kc = f"{Path.home()}/.kube/config_{cluster.name}"
    if temp_kube_config:
        _, temp_file = tempfile.mkstemp(prefix=f"ocl.{cluster.name}.")
        shutil.copyfile(kc, temp_file)
        return temp_file
    return kc


def run(
    cmd: list[str] | str,
    *,
    shell: bool = False,
    check: bool = True,
    capture_output: bool = True,
    cluster: Cluster | None = None,
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


def oc_login(cluster: Cluster, token: str) -> None:
    run(
        ["oc", "login", f"--token={token}", f"--server={cluster.server_url}"],
        cluster=cluster,
    )


def oc_project(cluster: Cluster, project: str) -> None:
    run(["oc", "project", project], cluster=cluster)


def oc_check_login(cluster: Cluster) -> bool:
    try:
        run(["oc", "cluster-info"], cluster=cluster)
        return True
    except subprocess.CalledProcessError:
        return False


def oc_setup(cluster: Cluster, idps: list[str], *, refresh_login: bool) -> None:
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

            hypershift = bool(cluster.spec.hypershift) if cluster.spec else False
            idp = select_idp(cluster.console_url, idps=idps) if not hypershift else None
            if idp or hypershift:
                with requests.Session() as session:
                    session.auth = HTTPKerberosAuth(mutual_authentication=OPTIONAL)
                    r = session.get(
                        token_request_url(
                            cluster.console_url, idp, hypershift=hypershift
                        )
                    )
                    r.raise_for_status()
                    form_data = pq(r.text)("form").serialize_dict()
                    r = session.post(
                        token_display_url(cluster.console_url, hypershift=hypershift),
                        data=form_data,
                    )
                    r.raise_for_status()
                    token = pq(r.text)("code")[0].text
            else:
                webbrowser.open(cluster.console_url)
                progress.stop()
                # manual login
                token = Prompt.ask("Enter token", password=True)
                progress.start()

            task = progress.add_task(description="CLI login ...", total=1)
            oc_login(cluster=cluster, token=token)
            progress.remove_task(task)


def blend_text(
    message: str, color1: tuple[int, int, int], color2: tuple[int, int, int]
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


def bye(*, quiet: bool) -> None:
    print(
        "Thank you for using openshift-login. :man_bowing: Have a great day ahead! :red_heart-emoji:",
        quiet=quiet,
    )


def enable_requests_logging() -> None:
    from http.client import HTTPConnection

    HTTPConnection.debuglevel = 1
    logging.getLogger().setLevel(logging.DEBUG)
    requests_log = logging.getLogger("urllib3")
    requests_log.setLevel(logging.DEBUG)
    requests_log.propagate = True


def complete_cluster(ctx: typer.Context, incomplete: str) -> Generator[str, None, None]:
    for cluster in clusters_from_app_interface():
        if cluster.name.startswith(incomplete):
            yield cluster.name


def complete_project(ctx: typer.Context, incomplete: str) -> Generator[str, None, None]:
    cluster = ctx.params.get("cluster_name")
    if not cluster:
        return
    for ns in [
        ns for ns in namespaces_from_app_interface() if ns.cluster.name == cluster
    ]:
        if ns.name.startswith(incomplete):
            yield ns.name


def print(msg: str | Text, *, quiet: bool) -> None:  # noqa: A001
    if quiet:
        return
    rich_print(msg)


@app.command(epilog="Made with :heart: by [blue]https://github.com/chassing[/]")
def main(  # noqa: C901
    cluster_name: str = typer.Argument(
        None,
        help="Cluster name",
        autocompletion=complete_cluster,
    ),
    project: str = typer.Argument(
        None,
        help="Namespace/Project",
        autocompletion=complete_project,
    ),
    *,
    debug: bool = typer.Option(default=False, help="Enable debug mode"),
    open_in_browser: bool = typer.Option(
        default=False, help="Open the console in browser instead of local shell"
    ),
    display_banner: bool = typer.Option(default=True, help="Display shiny OCL banner"),
    quiet: bool = typer.Option(default=False, help="Don't print anything"),
    refresh_login: bool = typer.Option(
        default=False, help="Enforce a new login to refresh the session."
    ),
    idp: list[str] = typer.Option(  # noqa: B008
        default=["redhat-app-sre-auth"],
        help="Automatically login via given IDPs (use in given order, try next one if failed). Use 'manual' for manual login.",
    ),
    command: str = typer.Option(
        default=os.environ["SHELL"],
        help="Run this command instead of spawning a new shell.",
    ),
) -> None:
    logging.basicConfig(
        level=logging.INFO if not debug else logging.DEBUG, format="%(message)s"
    )
    if debug:
        enable_requests_logging()

    print(
        blend_text(BANNER, (32, 32, 255), (255, 32, 255)),
        quiet=not display_banner or quiet,
    )

    if open_in_browser and cluster_name == ".":
        cluster_name = os.environ.get("OCL_CLUSTER_NAME", "")
        if not cluster_name:
            print(
                "[bold red]environment variable OCL_CLUSTER_NAME not set", quiet=quiet
            )
            sys.exit(1)
        project = run(["oc", "project", "-q"]).stdout.decode("utf-8").strip()

    if cluster_name:
        cluster = select_cluster(cluster_name)
    else:
        ns = select_namespace()
        cluster = ns.cluster
        project = ns.name
    console_url = cluster.console_url

    if project:
        console_url += f"/k8s/cluster/projects/{project}"

    if open_in_browser:
        print(f"[bold green]Opening [/] {console_url}", quiet=quiet)
        subprocess.run(["open", console_url], check=False)  # noqa: S607
        bye(quiet=quiet)
        sys.exit(0)
    try:
        oc_setup(
            cluster,
            idps=idp,
            refresh_login=refresh_login,
        )
    except subprocess.CalledProcessError as e:
        print(f"[bold red]'oc login' failed![/]\nException: {e}", quiet=quiet)
        sys.exit(1)

    if project:
        try:
            oc_project(cluster=cluster, project=project)
        except subprocess.CalledProcessError:
            print(
                f"[bold red]Entering {project} failed! Maybe this project doesn't exist or you don't have proper permissions.[/]",
                quiet=quiet,
            )
            project = ""

    if command == os.environ["SHELL"]:
        print("Spawn new shell, use exit or CTRL+d to leave it!", quiet=quiet)
    print(
        f"""
    URL: {console_url}
    Cluster: [bold green] {cluster.name}[/]
    {f"Project: [bold yellow]☸ {project}[/]" if project else ""}""",
        quiet=quiet,
    )

    result = run(
        shlex.split(command),
        check=False,
        cluster=cluster,
        capture_output=False,
        temp_kube_config=True,
    )
    if result.returncode != 0:
        print(
            f"[bold red]Command failed with exit code {result.returncode}[/]",
            quiet=quiet,
        )
        sys.exit(result.returncode)
    bye(quiet=quiet)


if __name__ == "__main__":
    app()
