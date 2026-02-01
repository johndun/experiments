"""Tests for file converters."""

from hydrate.converters import convert_csv, convert_file, convert_jsonl, convert_tsv


class TestConvertCsv:
    def test_basic_csv(self):
        content = "name,value\nfoo,1\nbar,2"
        result = convert_csv(content)
        assert "| name | value |" in result
        assert "| --- | --- |" in result
        assert "| foo | 1 |" in result
        assert "| bar | 2 |" in result

    def test_empty_csv(self):
        result = convert_csv("")
        assert result == ""

    def test_headers_only_csv(self):
        content = "name,value"
        result = convert_csv(content)
        assert "| name | value |" in result
        assert "| --- | --- |" in result
        lines = result.strip().split("\n")
        assert len(lines) == 2

    def test_csv_with_pipe_character(self):
        content = "name,value\nfoo|bar,1"
        result = convert_csv(content)
        assert "foo\\|bar" in result

    def test_csv_with_missing_values(self):
        content = "a,b,c\n1,2\n3"
        result = convert_csv(content)
        assert "| 1 | 2 |  |" in result
        assert "| 3 |  |  |" in result


class TestConvertTsv:
    def test_basic_tsv(self):
        content = "name\tvalue\nfoo\t1\nbar\t2"
        result = convert_tsv(content)
        assert "| name | value |" in result
        assert "| foo | 1 |" in result

    def test_empty_tsv(self):
        result = convert_tsv("")
        assert result == ""


class TestConvertJsonl:
    def test_basic_jsonl(self):
        content = '{"name": "foo", "value": 1}\n{"name": "bar", "value": 2}'
        result = convert_jsonl(content)
        assert "| name | value |" in result
        assert "| foo | 1 |" in result
        assert "| bar | 2 |" in result

    def test_empty_jsonl(self):
        result = convert_jsonl("")
        assert result == ""

    def test_jsonl_with_missing_keys(self):
        content = '{"a": 1, "b": 2}\n{"a": 3}'
        result = convert_jsonl(content)
        assert "| 1 | 2 |" in result
        assert "| 3 |  |" in result

    def test_jsonl_with_extra_keys(self):
        content = '{"a": 1}\n{"a": 2, "b": 3}'
        result = convert_jsonl(content)
        lines = result.strip().split("\n")
        assert "| a |" in lines[0]
        assert "| b |" not in lines[0]


class TestConvertFile:
    def test_csv_extension(self, tmp_path):
        from pathlib import Path

        path = Path("test.csv")
        content = "a,b\n1,2"
        result = convert_file(path, content)
        assert "| a | b |" in result

    def test_tsv_extension(self, tmp_path):
        from pathlib import Path

        path = Path("test.tsv")
        content = "a\tb\n1\t2"
        result = convert_file(path, content)
        assert "| a | b |" in result

    def test_jsonl_extension(self, tmp_path):
        from pathlib import Path

        path = Path("test.jsonl")
        content = '{"a": 1}'
        result = convert_file(path, content)
        assert "| a |" in result

    def test_other_extension(self, tmp_path):
        from pathlib import Path

        path = Path("test.txt")
        content = "plain text content"
        result = convert_file(path, content)
        assert result == content

    def test_uppercase_extension(self, tmp_path):
        from pathlib import Path

        path = Path("test.CSV")
        content = "a,b\n1,2"
        result = convert_file(path, content)
        assert "| a | b |" in result
