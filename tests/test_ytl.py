import unittest

from bs4 import BeautifulSoup

from lib import Subject, YtlDatum
from ytl import _extract_point_links, _parse_subject_row


class YtlParsingTests(unittest.TestCase):
    def test_extract_point_links_filters_to_supported_years(self):
        html = """
        <a class="main-menu__link" href="/old">Pisterajat kevät 2020</a>
        <a class="main-menu__link" href="/spring-2021">Pisterajat kevät 2021</a>
        <a class="main-menu__link" href="https://www.ylioppilastutkinto.fi/fall-2022">Pisterajat syksy 2022</a>
        """

        self.assertEqual(
            _extract_point_links(html),
            [
                ("2021 kevät", "https://www.ylioppilastutkinto.fi/spring-2021"),
                ("2022 syksy", "https://www.ylioppilastutkinto.fi/fall-2022"),
            ],
        )

    def test_parse_subject_row_normalizes_points(self):
        subject = Subject("Fysiikka", "Fysiikka", 120)
        row = BeautifulSoup(
            """
            <tr>
              <td>Fysiikka</td>
              <td>113</td>
              <td>102</td>
              <td>91</td>
              <td>80</td>
              <td>67</td>
              <td>52</td>
            </tr>
            """,
            "html.parser",
        ).find("tr")

        self.assertEqual(
            _parse_subject_row(row, "2024 kevät", subject),
            [
                YtlDatum("2024 kevät", "Fysiikka", "L", 113 / 120),
                YtlDatum("2024 kevät", "Fysiikka", "E", 102 / 120),
                YtlDatum("2024 kevät", "Fysiikka", "M", 91 / 120),
                YtlDatum("2024 kevät", "Fysiikka", "C", 80 / 120),
                YtlDatum("2024 kevät", "Fysiikka", "B", 67 / 120),
                YtlDatum("2024 kevät", "Fysiikka", "A", 52 / 120),
            ],
        )

    def test_parse_subject_row_rejects_short_rows(self):
        subject = Subject("Fysiikka", "Fysiikka", 120)
        row = BeautifulSoup("<tr><td>Fysiikka</td><td>113</td></tr>", "html.parser").find("tr")

        with self.assertRaisesRegex(ValueError, "Unexpected point table format"):
            _parse_subject_row(row, "2024 kevät", subject)


if __name__ == "__main__":
    unittest.main()
