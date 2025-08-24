from pathlib import Path

from dagtool.conf import YamlConf


def test_yaml_conf_variables(test_path: Path):
    p: Path = test_path.parent / "dags/demo"
    yaml_loader = YamlConf(path=p)
    print(yaml_loader.read_variable("01_start", stage="dev"))
