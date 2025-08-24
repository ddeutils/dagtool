from functools import partial
from pathlib import Path

from dagtool.conf import YamlConf
from dagtool.models import get_variable_stage, read_variable


def test_yaml_conf_variables(test_path: Path):
    p: Path = test_path.parent / "dags/demo"
    var = partial(
        read_variable,
        path=p,
        name="03_template",
    )
    assert var("project_id") == "stock-data-dev-399709"
    assert var("start_date") == "2022-06-16 00:00:00 Asia/Bangkok"


def test_get_variable_stage(test_path: Path):
    p: Path = test_path.parent / "dags/demo"
    var = get_variable_stage(path=p, name="03_template")
    print(var.get("project_id"))


def test_yaml_conf_dags(test_path: Path):
    p: Path = test_path.parent / "dags/demo"
    yaml_loader = YamlConf(path=p)
    conf = yaml_loader.read_conf()
    assert len(conf) == 3
    print(conf[2])
