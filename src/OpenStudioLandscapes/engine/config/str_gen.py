from typing import Type

from pydantic_core._pydantic_core import PydanticUndefinedType

import yaml
import json
import pydantic

from dagster import get_dagster_logger

LOGGER = get_dagster_logger(__name__)


def get_config_str(
        Config: Type[pydantic.BaseModel],
) -> str:
    LOGGER.info(f"{Config.model_fields = }")

    doc_str = str()

    field_k: str
    field_v: pydantic.FieldInfo

    for field_k, field_v in Config.model_fields.items():
        try:
            LOGGER.info(f"{field_k = }")
            LOGGER.info(f"{field_v.is_required() = }")
            # LOGGER.debug(f"Field name: {field_k}")

            # LOGGER.debug(f"\tValues specified in Config:")

            sub_class_required = field_v.is_required()
            sub_class_value = field_v.default
            sub_class_annotation = field_v.annotation
            sub_class_description = str(field_v.description)
            sub_class_examples = str(field_v.examples)
            # LOGGER.debug(f"\t\tType: {annotation}")
            # LOGGER.debug(f"\t\tValue: {sub_class_value}")
            # LOGGER.debug(f"\t\tDescription: {sub_class_description}")

            doc_str += f"# {''.rjust(len(field_k), '=')}\n"
            doc_str += f"# {field_k}\n"
            doc_str += f"# {''.rjust(len(field_k), '-')}\n"
            doc_str += f"#\n"
            doc_str += f"# Type: {sub_class_annotation}\n"

            if field_k in Config.__base__.model_fields:
                # print(f"\tDefault Value: {Config.__base__.model_fields[field_k] = }")
                base_class_required = Config.__base__.model_fields[field_k].is_required()
                base_class_value = Config.__base__.model_fields[field_k].default
                # base_class_annotation = Config.__base__.model_fields[field_k].annotation
                base_class_description = Config.__base__.model_fields[field_k].description
                # LOGGER.debug(f"\t\tType: {base_class_annotation}")
                # LOGGER.debug(f"\t\tDefault Value: {base_class_value}")
                # LOGGER.debug(f"\t\tDefault Description: {base_class_description}")

                doc_str += (f"# Base Class Info:\n"
                            f"#     Required:\n"
                            f"#         {base_class_required}\n"
                            f"#     Description:\n"
                            f"#         {base_class_description}\n"
                            f"#     Default value:\n"
                            f"#         {base_class_value}\n")

            doc_str += (f"# Description:\n"
                        f"#     {sub_class_description}\n"
                        f"# Required:\n"
                        f"#     {sub_class_required}\n"
                        f"# Examples:\n"
                        f"#     {sub_class_examples}\n")

            if base_class_value == sub_class_value:
                doc_str += f"\n\n"
                continue

            # LOGGER.error(f"{sub_class_value = }")
            # LOGGER.error(f"{type(sub_class_value) = }")

            if isinstance(sub_class_value, PydanticUndefinedType):
                kv = {field_k: "REQUIRED (CHANGE_ME)"}
            else:
                kv = {field_k: sub_class_value}

            doc_str += f"{yaml.safe_dump(json.loads(json.dumps(kv, indent=2, default=str)))}\n\n"

        except Exception as e:
            LOGGER.error(f"{e}")
            raise Exception from e

    return doc_str.rstrip()  # strip trailing newlines


# if "__main__" == __name__:
#
#     import ruamel.yaml as ruaml
#     import yaml
#     import sys
#     # test = Config(**{})
#
#     logging.basicConfig(level=logging.DEBUG)
#
#     # LOGGER.setLevel(logging.DEBUG)
#
#     LOGGER.debug(Config.model_fields)
#
#     doc_str = str()
#
#     for field_k, field_v in Config.model_fields.items():
#         # if field_k in super(Config).model_fields:
#         LOGGER.debug(f"Field name: {field_k}")
#         # print(f"{field_v = }")
#         # print(f"required = {Config.model_fields[field_k].required}")
#         # print(f"required = {Config.__base__.model_fields[field_k].required}")
#
#         default_value = None
#         default_annotation = None
#         default_description = None
#
#         # print(f"\tValues inherited from Base Class:")
#         if field_k in Config.__base__.model_fields:
#             # print(f"\tDefault Value: {Config.__base__.model_fields[field_k] = }")
#             default_value = Config.__base__.model_fields[field_k].default
#             default_annotation = Config.__base__.model_fields[field_k].annotation
#             default_description = Config.__base__.model_fields[field_k].description
#             LOGGER.debug(f"\t\tType: {default_annotation}")
#             LOGGER.debug(f"\t\tDefault Value: {default_value}")
#             LOGGER.debug(f"\t\tDefault Description: {default_description}")
#
#         LOGGER.debug(f"\tValues specified in Config:")
#         # print(f"\tDefault Value: {Config.__base__.model_fields[field_k] = }")
#         value = field_v.default
#         annotation = field_v.annotation
#         description = str(field_v.description)
#         LOGGER.debug(f"\t\tType: {annotation}")
#         LOGGER.debug(f"\t\tValue: {value}")
#         LOGGER.debug(f"\t\tDescription: {description}")
#
#         if default_value == value:
#             continue
#
#         doc_str += (f"# Type: {annotation}\n"
#                     f"# Description:\n"
#                     f"# {description}\n")
#         # try:
#         # doc_str += f"{field_k}: {yaml.safe_dump(json.loads(json.dumps(Config.model_fields[field_k].default, indent=2, default=str)))}\n\n"
#         # doc_str += f"{yaml.safe_dump(json.loads(json.dumps({Config.model_fields[field_k].default}, indent=2, default=str)))}\n\n"
#         doc_str += f"{yaml.safe_dump(json.loads(json.dumps({field_k: value}, indent=2, default=str)))}\n"
#         # except AttributeError:
#         #     doc_str += f"{json.dumps(getattr(Config.__base__.model_fields, field_k), indent=2, default=str)}\n\n"
#             # continue
#         # print(field_k)
#         # print(f"{field_v = }")
#
#
#     yaml = ruaml.YAML(typ="rt")
#     print(doc_str)
#     # code = yaml.load(doc_str)
#     # yaml.dump(code, sys.stdout)