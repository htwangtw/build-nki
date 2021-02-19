from pathlib import Path

import pytest
from click.testing import CliRunner

from publiccrawler.crawler import subject_crawler, parse_line, save_addurls_table
from publiccrawler.cli import main

s3_bucket_name = 'openneuro'
bids_prefix = 'ds000003/ds000003_R2.0.2/uncompressed'


def test_parse_line():
    content = 'data/sub-01/func/sub-01_task-rest_bold.nii.gz'
    row = parse_line(s3_bucket_name, content)
    assert row[0] == f"s3://{s3_bucket_name}/{content}"
    assert row[1] == f"s3://{s3_bucket_name}/data"
    assert row[2] == "sub-01"
    assert row[3] == "func/sub-01_task-rest_bold.nii.gz"

def test_crawler(tmpdir):
    sub = "sub-03"
    collect_files = subject_crawler(s3_bucket_name, bids_prefix, sub)
    for f in collect_files:
        assert type(f) == str
    out = Path(tmpdir)
    save_addurls_table(collect_files[:2],
                       s3_bucket_name, out / "sub-03.tsv")
    assert (out / "sub-03.tsv").is_file()
    with open(out / "sub-03.tsv") as f:
        data = f.readlines()
    assert len(data) == 3


@pytest.fixture
def runner():
    return CliRunner()

def test_beh2bids(runner, tmpdir):
    result = runner.invoke(main,
        ["--s3bucket", s3_bucket_name,
         "--prefix", bids_prefix,
         "--output", tmpdir,
         "sub-01"])
    assert result.exit_code == 0

    result = runner.invoke(main, ["--help"])
    assert "stuff" in result.output
    assert result.exit_code == 0
