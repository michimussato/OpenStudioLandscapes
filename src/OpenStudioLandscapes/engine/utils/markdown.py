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
    gh_path = "/".join([
        repo_,
        "blob",
        "main",
        parts_[-4],
        parts_[-3],
        module_,
        file_
    ])

    doc = snakemd.Document()

    # TOC

    doc.add_table_of_contents(
        levels=range(1, 3)
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

    ## Variables

    doc.add_heading(
        text="Variables",
        level=2,
    )

    doc.add_paragraph(
        text=textwrap.dedent(
            f"""
            The following variables are being declared in 
            [`{constants._module}`](https://github.com/michimussato/{gh_path}) published throuout the `{repo_}` package.
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
        "Value"
    ]

    rows_environment = []

    for k, v in constants.ENVIRONMENT.items():
        # print(json.dumps(val, indent=4))

        rows_environment.append(
            [
                snakemd.Inline(
                    text=k,
                ).code(),
                snakemd.Inline(
                    text=type(v).__name__,
                ).code(),
                snakemd.Inline(
                    text=v,
                ).code(),
            ]
        )

    doc.add_table(
        header=header_environment,
        data=rows_environment,
        align=[
            snakemd.Table.Align.LEFT,
            snakemd.Table.Align.LEFT,
            snakemd.Table.Align.LEFT,
        ],
        indent=0,
    )

    # doc.dump("README_TEST")
    doc.dump(str(pathlib.Path(rel_path).parent.parent.parent.parent / "README_TEST"))


if __name__ == "__main__":
    pass
    # from OpenStudioLandscapes.Kitsu import constants
    # main(constants=constants)
    # main(path="/home/michael/git/repos/OpenStudioLandscapes-Kitsu/src/OpenStudioLandscapes/Kitsu/constants.py")
