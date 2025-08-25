from pathlib import Path

from airflow.templates import NativeEnvironment
from jinja2 import Environment

from dagtool.conf import YamlConf
from dagtool.models import get_variable_stage


def test_get_variable_stage(test_path: Path):
    p: Path = test_path / "demo"
    var = get_variable_stage(path=p, name="unittest")
    assert var.get("project_id") == "stock-data-dev-399709"
    assert var.get("not-exits", "default") == "default"


def test_pass_variable_with_jinja(test_path: Path):
    p: Path = test_path / "demo"
    var = get_variable_stage(path=p, name="unittest")

    env: Environment = NativeEnvironment()
    env.globals.update({"var": var.get})

    template = env.from_string("{{ var('project_id') }}")
    data = template.render()
    print(data)


def test_yaml_conf_dags(test_path: Path):
    p: Path = test_path.parent / "dags/demo"
    yaml_loader = YamlConf(path=p)
    conf = yaml_loader.read_conf()
    assert len(conf) == 3
    print(conf[2])
