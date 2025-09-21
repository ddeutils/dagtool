from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import Any

from jinja2 import Environment, Template, Undefined
from jinja2.nativetypes import NativeEnvironment
from typing_extensions import Self


class JinjaRender:
    """Jinja Render object.

    This object use for common create Jinja environment and template any component
    outside Airflow template.
    """

    def __init__(
        self,
        template_fields: Sequence[str],
        template_excluded_fields: Sequence[str] | None = None,
        template_nested_fields: Sequence[str] | None = None,
        jinja_environment_kwargs: dict[str, Any] | None = None,
        user_defined_filters: dict[str, Callable] | None = None,
        user_defined_macros: dict[str, Callable | str] | None = None,
    ) -> None:
        """Main initialize construct method.

        Args:
            template_fields (Sequence[str]): A sequence of fields that want to
                pass a Jinja template.
            template_excluded_fields (Sequence[str]): A sequence of fields that
                want to not pass a Jinja template.
            template_nested_fields (Sequence[str]): A sequence of fields that
                pass nested Jinja template again with the same template fields
                setting sequence.
            jinja_environment_kwargs:
            user_defined_filters (dict[str, Callable]): An user defined Jinja
                template filters that will add to Jinja environment.
            user_defined_macros (dict[str, Callable | str]): An user defined
                Jinja template macros that will add to Jinja environment.
        """
        self.template_fields: Sequence[str] = template_fields
        self.template_excluded_fields: Sequence[str] = (
            template_excluded_fields or []
        )
        self.template_nested_fields: Sequence[str] = (
            template_nested_fields or []
        )
        self.user_defined_filters = user_defined_filters or {}
        self.user_defined_macros = user_defined_macros or {}

        # NOTE: Start create the Jinja Environment object.
        self.env: Environment = self.get_template_env(
            user_defined_macros=user_defined_macros,
            user_defined_filters=user_defined_filters,
            jinja_environment_kwargs=jinja_environment_kwargs,
        )

    def set_globals(self, values: dict[str, Any]) -> Self:
        """Update the Jinja Environment globals value.

        Args:
            values (dict[str, Any]): A mapping value that want to update to the
                current globals Jinja environment.
        """
        self.env.globals.update(values)
        return self

    def render_template(self, data: Any, env: Environment | None = None) -> Any:
        """Render template to the value that its key that exists in the
        ``template_fields`` class variable.

        Args:
            data (Any): Any data that want to render Jinja template.
            env (Environment): A Jinja environment.

        Returns:
            Any: A data that already pass Jinja template from the current Jinja
                environment.
        """
        if not isinstance(data, dict):
            return self._render(data, env=env or self.env)

        for key in data:
            # NOTE: Start nested render the Jinja template for the specific key
            #   such as `default_args` value.
            if key in self.template_nested_fields:
                data[key] = self.render_template(data[key], env=env or self.env)
                continue

            if (
                key in self.template_excluded_fields
                or key not in self.template_fields
            ):
                continue

            data[key] = self._render(data[key], env=env or self.env)
        return data

    def _render(self, value: Any, env: Environment) -> Any:
        """Render Jinja template to any value with the current Jinja environment.

            This private method will check the type of value before make Jinja
        template and render it before returning.

        Args:
            value (Any): An any value.
            env (Environment): A Jinja environment object.

        Returns:
            Any: The value that was rendered if it is string type.
        """
        if isinstance(value, str):
            template: Template = env.from_string(value)
            return template.render()

        if value.__class__ is tuple:
            return tuple(self._render(element, env) for element in value)
        elif isinstance(value, tuple):
            return value.__class__(*(self._render(el, env) for el in value))
        elif isinstance(value, list):
            return [self._render(element, env) for element in value]
        elif isinstance(value, dict):
            return {k: self._render(v, env) for k, v in value.items()}
        elif isinstance(value, set):
            return {self._render(element, env) for element in value}

        return value

    def get_template_env(
        self,
        *,
        user_defined_filters: dict[str, Callable] | None = None,
        user_defined_macros: dict[str, Callable | str] | None = None,
        jinja_environment_kwargs: dict[str, Any] | None = None,
    ) -> Environment:
        """Return Jinja Template Native Environment object for render template
        to the Dag parameters before create Airflow DAG.

        Args:
            user_defined_filters (dict[str, Callable]): An user defined Jinja
                template filters that will add to Jinja environment.
            user_defined_macros (dict[str, Callable | str]): An user defined
                Jinja template macros that will add to Jinja environment.
            jinja_environment_kwargs: Additional configuration options to be
                passed to Jinja `Environment` for template rendering.

        Returns:
            Environment: A Jinja Environment instance.
        """
        # NOTE: This setting reference from Airflow DAG Jinja environment setup.
        jinja_env_options: dict[str, Any] = {
            "undefined": Undefined,
            "extensions": ["jinja2.ext.do"],
            "cache_size": 0,
        }
        env: Environment = NativeEnvironment(
            **(jinja_env_options | (jinja_environment_kwargs or {}))
        )
        udf_macros: dict[str, Any] = self.user_defined_macros | (
            user_defined_macros or {}
        )
        if udf_macros:
            env.globals.update(udf_macros)
        udf_filters: dict[str, Any] = self.user_defined_filters | (
            user_defined_filters or {}
        )
        if udf_filters:
            env.filters.update(udf_macros)
        return env
