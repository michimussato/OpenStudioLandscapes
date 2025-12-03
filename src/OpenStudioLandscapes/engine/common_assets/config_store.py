#
#
#
# @asset(
#     **ASSET_HEADER,
#     description=textwrap.dedent(
#         """
#         Loads the default `config.yml` that comes with
#         the Feature itself. Contents are being validated
#         against a `pydantic.BaseModel` in this step.
#         """
#     )
# )
# def CONFIG_DEFAULT(
#     context: AssetExecutionContext,
# ) -> Generator[
#     Output[str] | AssetMaterialization,
#     None,
#     None,
# ]:
#
#     with open(pathlib.Path(__file__).parent / "config.yml") as fr:
#         # This is str so that comments are read as well
#         config_str: str = fr.read()
#
#     # with open(pathlib.Path(__file__).parent / "config.yml") as fr:
#     config = yaml.safe_load(config_str)
#
#     # context.log.debug(f"{config = }")
#
#     try:
#         context.log.info(f"Validating: {config = }")
#         _config_validated = Config(**config)
#         context.log.debug(f"Validated.")
#     except ValidationError as err:
#         context.log.error(
#             "Config Validation failed. "
#             "The default `config.yml` for "
#             f"{FEATURE} contains "
#             "errors, missing and/or illegal parameters."
#         )
#         raise ValidationError from err
#
#     yield Output(config_str)
#
#     diff = DeepDiff(
#         config,
#         # We don't want to compare expanded
#         # with non-expanded dicts - creates too
#         # much noise in the diff
#         _config_validated.model_dump(mode="json")
#     )
#
#     yield AssetMaterialization(
#         asset_key=context.asset_key,
#         metadata={
#             "__".join(context.asset_key.path): MetadataValue.md(f"```yaml\n{config_str}\n```"),
#             "diff": MetadataValue.md(f"```json\n{json.dumps(diff, indent=2, default=str)}\n```"),
#         },
#     )
#
#
# @asset(
#     **ASSET_HEADER,
#     ins={
#         "env": AssetIn(
#             AssetKey([*ASSET_HEADER["key_prefix"], "env"]),
#         ),
#         "CONFIG_DEFAULT": AssetIn(
#             AssetKey([*ASSET_HEADER["key_prefix"], "CONFIG_DEFAULT"]),
#         ),
#     },
#     description=textwrap.dedent(
#         """
#         Reads options from a custom `config.yml`.
#         If the custom `config.yml` does not exist, it
#         will be created locally containing default options.
#         """
#     )
# )
# def CONFIG_STORE(
#     context: AssetExecutionContext,
#     env: dict,  # pylint: disable=redefined-outer-name
#     CONFIG_DEFAULT: str,  # pylint: disable=redefined-outer-name
# ) -> Generator[
#     Output[Config]
#     | AssetMaterialization,
#     None,
#     None,
# ]:
#
#     configs_root = pathlib.Path(EnvVar("OPENSTUDIOLANDSCAPES__CONFIGSTORE_ROOT").get_value(), f"{ASSET_HEADER['group_name']}__{'__'.join(ASSET_HEADER['key_prefix'])}").expanduser().resolve()
#     config_yml = pathlib.Path(configs_root / "config.yml")
#     configs_root.mkdir(parents=True, exist_ok=True)
#
#     # config_result = CONFIG_DEFAULT.copy()
#     config_default_ = yaml.safe_load(CONFIG_DEFAULT)
#
#     # This is valid as we checked it already
#     config_base = Config(**config_default_)
#
#     if not config_yml.exists():
#         context.log.info(
#             f"No existing config file found. "
#             f"Creating {config_yml.as_posix()}..."
#         )
#         with open(config_yml, "w") as fw:
#             # Just write the exact same
#             # contents to the new file
#             fw.write(CONFIG_DEFAULT)
#             # No need to re-validate
#             # config_validated = Config(**config_base)
#     else:
#         context.log.info(f"Skipping config file creation.")
#
#     context.log.info(
#         f"Reading {config_yml.as_posix()}..."
#     )
#     with open(config_yml, "r") as fr:
#         config_store = yaml.safe_load(fr)
#
#         try:
#             context.log.info(f"Validating: {config_store = }")
#             config_store_validated = Config(
#                 # Layer the dicts on top of each other
#                 # to create the resulting Config
#                 # Todo:
#                 #  - [ ] is that a safe operation?
#                 **{
#                     **config_default_,
#                     **config_store,
#                 }
#             )
#             context.log.debug(f"Validated.")
#         except ValidationError as err:
#             context.log.error(
#                 "Config Validation failed. "
#                 f"The custom `config.yml` ({config_yml.as_posix()}) for "
#                 f"{FEATURE} contains "
#                 "errors, missing and/or illegal parameters."
#             )
#             raise ValidationError from err
#
#     config = config_store_validated.model_dump(mode="python")
#     # config.update(config_store_validated.model_dump(mode="python"))
#
#     config_expanded = expand_dict_vars(
#         dict_to_expand=config.copy(),
#         kv={
#             "GROUP": ASSET_HEADER["group_name"],
#             "KEY": '__'.join(ASSET_HEADER["key_prefix"]),
#             "FEATURE": FEATURE,
#             **env,
#         },
#     )
#
#     # context.log.debug(f"{config_expanded = }")
#
#     try:
#         # Final validation of the parsed configs
#         context.log.info(f"Validating: {config_expanded = }")
#         config_validated = Config(**config_expanded)
#         context.log.debug(f"Validated.")
#     except ValidationError as err:
#         context.log.error(
#             "Config Validation failed. "
#             f"The parsed config for "
#             f"{FEATURE} contains "
#             "errors, missing and/or illegal parameters."
#         )
#         raise ValidationError from err
#
#     yield Output(config_validated)
#
#     diff = DeepDiff(
#         t1={
#             **config_store,
#             **config_base.model_dump(mode="json")},
#         # We don't want to compare expanded
#         # with non-expanded dicts - creates too
#         # much noise in the diff
#         t2={
#             **config_store_validated.model_dump(mode="json"),
#         },
#     )
#
#     yield AssetMaterialization(
#         asset_key=context.asset_key,
#         metadata={
#             # "__".join(context.asset_key.path): MetadataValue.json(config_validated.model_dump(mode="json")),
#             "__".join(context.asset_key.path): MetadataValue.md(f"```json\n{json.dumps(config_validated.model_dump(mode='json'), indent=2, default=str)}\n```"),
#             "config_yml": MetadataValue.path(config_yml),
#             # "config_raw": MetadataValue.json(json.loads(json.dumps(config, default=str))),
#             "config_raw": MetadataValue.md(f"```json\n{json.dumps(config, indent=2, default=str)}\n```"),
#             # "config_resolved": MetadataValue.json(json.loads(json.dumps(config_expanded, default=str))),
#             # "diff": MetadataValue.json(json.loads(json.dumps(diff, default=str))),
#             "diff": MetadataValue.md(f"```json\n{json.dumps(diff, indent=2, default=str)}\n```"),
#         },
#     )