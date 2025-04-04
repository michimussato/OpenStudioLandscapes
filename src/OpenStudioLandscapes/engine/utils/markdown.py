import json
import textwrap
import snakemd
import pathlib


def main(constants):

    rel_path = pathlib.Path(constants.__file__)
    parts_ = rel_path.parts

    file_ = parts_[-1]
    module_ = parts_[-2]
    repo_ = parts_[-5]

    gh_prefix = "https://github.com/michimussato/"

    gh_repo = f"{gh_prefix}{repo_}.git"

    gh_path_constants = "/".join([
        repo_,
        # "blob",
        "tree",
        "main",
        parts_[-4],
        parts_[-3],
        module_,
        file_
    ])

    gh_path_noxfile = "/".join([
        repo_,
        "tree",
        "main",
        "noxfile.py",
    ])

    gh_path_sbom = "/".join([
        repo_,
        "tree",
        "main",
        ".sbom",
    ])

    doc = snakemd.Document()

    # TOC

    doc.add_table_of_contents(
        levels=range(1, 4)
    )

    doc.add_horizontal_rule()

    # Title

    doc.add_heading(
        text=module_,
        level=1,
    )

    ## Brief

    doc.add_heading(
        text="Brief",
        level=2,
    )

    ### Logo

    doc.add_paragraph(
        snakemd.Inline(
            text=textwrap.dedent(
                """
                Logo OpenStudioLandscapes
                """
            ),
            image={
                "OpenStudioLandscapes": "https://github.com/michimussato/OpenStudioLandscapes/raw/main/_images/logo128.png",
                "test": "https://www.snakemd.io/en/latest/_static/icon.png"
            }["OpenStudioLandscapes"],
            link="https://github.com/michimussato/OpenStudioLandscapes",
        ).__str__()
    )

    ### Text

    doc.add_paragraph(
        text=textwrap.dedent(
            """
            This is an extension to the OpenStudioLandscapes ecosystem. The full documentation of 
            OpenStudioLandscapes is available [here](https://github.com/michimussato/OpenStudioLandscapes).
            """
        )
    )

    ## Install

    doc.add_heading(
        text="Install",
        level=2,
    )

    ### From Github directly

    doc.add_heading(
        text="From Github directly",
        level=3,
    )
    # Todo:
    #  - [ ] OpenStudioLandscapes[dev] @ git+https://github.com/michimussato/OpenStudioLandscapes.git@main

    doc.add_paragraph(
        text=textwrap.dedent(
            """
            WIP: This does not work as expected yet.
            """
        )
    )

    doc.add_paragraph(
        text=textwrap.dedent(
            """
            For more info see [VCS Support of pip](https://pip.pypa.io/en/stable/topics/vcs-support/).
            """
        )
    )

    # str_ = "\\'{repo_}[dev] @ git+{gh_repo}@main\\'"

    # doc.add_code(
    #     code=textwrap.dedent(
    #         f"""
    #         pip install -U
    #         """
    #     ),
    #     lang="shell",
    # )

    ### From local Repo

    doc.add_heading(
        text="From local Repo",
        level=3,
    )

    doc.add_paragraph(
        text=textwrap.dedent(
            """
            Clone repository:
            """
        )
    )

    doc.add_code(
        code=textwrap.dedent(
            f"""
            git clone {gh_repo}
            cd {repo_}
            """
        ),
        lang="shell",
    )

    doc.add_paragraph(
        text=textwrap.dedent(
            """
            Create venv, activate it and upgrade:
            """
        )
    )

    doc.add_code(
        code=textwrap.dedent(
            f"""
            python3.11 -m venv .venv
            source .venv/bin/activate
            pip install setuptools --upgrade
            """
        ),
        lang="shell",
    )

    doc.add_code(
        code=textwrap.dedent(
            f"""
            pip install -e .[dev]
            """
        ),
        lang="shell",
    )

    doc.add_paragraph(
        text=textwrap.dedent(
            """
            For more info see [VCS Support of pip](https://pip.pypa.io/en/stable/topics/vcs-support/).
            """
        )
    )

    ## Add to OpenStudioLandscapes

    doc.add_heading(
        text="Add to OpenStudioLandscapes",
        level=2,
    )

    doc.add_paragraph(
        text=textwrap.dedent(
            """
            Add the following code to `OpenStudioLandscapes.engine.constants` (`THIRD_PARTY`):
            """
        )
    )

    doc.add_code(
        code=textwrap.dedent(
            """
            THIRD_PARTY.append(
               {
                  "enabled": True,
                  "module": "%s.definitions",
                  "compose_scope": ComposeScope.DEFAULT,
               }
            )
            """
        ) % str(constants._module).replace(".constants", ""),  # Todo: a bit hacky
        lang="python",
    )

    ## Testing

    doc.add_heading(
        text="Testing",
        level=2,
    )

    ### pre-commit

    doc.add_heading(
        text="pre-commit",
        level=3,
    )

    doc.add_unordered_list(
        [
            "https://pre-commit.com",
            "https://pre-commit.com/hooks.html",
        ]
    )

    doc.add_code(
        code=textwrap.dedent(
            """
            pre-commit install
            """
        ),
        lang="shell",
    )

    ### nox

    doc.add_heading(
        text="nox",
        level=3,
    )

    doc.add_code(
        code=textwrap.dedent(
            """
            nox --no-error-on-missing-interpreters --report .nox/nox-report.json
            """
        ),
        lang="shell",
    )

    ### Pylint

    doc.add_heading(
        text="pylint",
        level=3,
    )

    doc.add_heading(
        text="pylint: disable=redefined-outer-name",
        level=4,
    )

    doc.add_unordered_list(
        [
            "[`W0621`](https://pylint.pycqa.org/en/latest/user_guide/messages/warning/redefined-outer-name.html): Due to Dagsters way of piping arguments into assets.",
        ]
    )

    ### SBOM

    doc.add_heading(
        text="SBOM",
        level=3,
    )

    doc.add_paragraph(
        text=textwrap.dedent(
            """
            Acronym for Software Bill of Materials
            """
        )
    )

    doc.add_paragraph(
        text=textwrap.dedent(
            """
            We create the following SBOMs:
            """
        )
    )

    doc.add_unordered_list(
        [
            "[`cyclonedx-bom`](https://pypi.org/project/cyclonedx-bom/)",
            "[`pipdeptree`](https://pypi.org/project/pipdeptree/) (Dot)",
            "[`pipdeptree`](https://pypi.org/project/pipdeptree/) (Mermaid)",
        ]
    )

    doc.add_paragraph(
        text=textwrap.dedent(
            f"""
            SBOMs for the different Python interpreters defined in [`.noxfile.VERSIONS`]({gh_prefix}{gh_path_noxfile}) 
            will be created in [`.sbom`]({gh_prefix}{gh_path_sbom})
            """
        )
    )

    doc.add_paragraph(
        text=textwrap.dedent(
            f"""
            Currently, the following Python interpreters are enabled for testing:
            """
        )
    )

    doc.add_unordered_list(
        [
            "`cyclone-dx`",
            "`pipdeptree` (Dot)",
            "`pipdeptree` (Mermaid)",
        ]
    )

    ## Variables

    doc.add_heading(
        text="Variables",
        level=2,
    )

    doc.add_paragraph(
        text=textwrap.dedent(
            f"""
            The following variables are being declared in 
            [`{constants._module}`]({gh_prefix}{gh_path_constants}) published throuout the `{repo_}` package.
            """
        )
    )

    header = [
        "Variable",
        "Type"
    ]

    rows = []

    for var in constants.__all__:
        val = constants.__dict__[var]
        # print(json.dumps(val, indent=4))

        rows.append(
            [
                snakemd.Inline(
                    text=var,
                ).code(),
                snakemd.Inline(
                    text=type(val).__name__,
                ).code(),
            ]
        )

    doc.add_table(
        header=header,
        data=rows,
        align=[
            snakemd.Table.Align.LEFT,
            snakemd.Table.Align.LEFT,
        ],
        indent=0,
    )

    ### ENVIRONMENT

    doc.add_heading(
        text="Environment",
        level=3,
    )

    header_environment = [
        "Variable",
        "Type",
        # "Value"
    ]

    rows_environment = []

    for k, v in constants.ENVIRONMENT.items():

        rows_environment.append(
            [
                snakemd.Inline(
                    text=k,
                ).code(),
                snakemd.Inline(
                    text=type(v).__name__,
                ).code(),
                # snakemd.Inline(
                #     text=v,
                # ).code(),
            ]
        )

    doc.add_table(
        header=header_environment,
        data=rows_environment,
        align=[
            snakemd.Table.Align.LEFT,
            snakemd.Table.Align.LEFT,
            # snakemd.Table.Align.LEFT,
        ],
        indent=0,
    )

    doc.dump(str(pathlib.Path(rel_path).parent.parent.parent.parent / "README"))


if __name__ == "__main__":
    pass
