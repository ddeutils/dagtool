from pathlib import Path

from jinja2 import Environment
from jinja2.nativetypes import NativeEnvironment

from dagtool.loader import YamlConf
from dagtool.models.dag import Variable


def test_get_variable_stage(test_path: Path):
    p: Path = test_path / "demo"
    var = Variable.from_path_with_key(path=p, key="unittest")
    assert var.get("project_id") == "stock-data-dev"
    assert var.get("not-exits", "default") == "default"


def test_pass_variable_with_jinja(test_path: Path):
    p: Path = test_path / "demo"
    var = Variable.from_path_with_key(path=p, key="unittest")

    env: Environment = NativeEnvironment()
    env.globals.update({"var": var.get})

    template = env.from_string("{{ var('project_id') }}")
    data = template.render()
    print(data)


def test_yaml_conf_dags(test_path: Path):
    p: Path = test_path.parent / "dags/demo"
    yaml_loader = YamlConf(path=p)
    conf = yaml_loader.read_conf()
    assert len(conf) == 4
    print(conf[2])
