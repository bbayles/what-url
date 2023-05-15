from unittest import TestCase

from what_url import (
    check_url,
    join_url,
    normalize_url,
    parse_url,
    replace_url,
)


class WhatURLTests(TestCase):
    def test_check_url(self):
        for s, expected in (
            ('https:example.org', True),
            ('https://////example.com/// ', True),
            ('https://example.com/././foo', True),
            ('file:///C|/demo', True),
            ('https://127.0.0.1./', True),
            ('bogus', False),
            ('https://exa%23mple.org', False),
            ('foo://exa[mple.org', False),
            ('https://127.0.0.0.1./', False),
            (None, False),
            (1, False),
            ('', False),
            ('\n', False),
        ):
            with self.subTest(s=s):
                actual = check_url(s)
                self.assertEqual(actual, expected)

    def test_join_url(self):
        # Tests from https://www.rfc-editor.org/rfc/rfc3986.html
        # sections 5.4.1. and 5.4.2
        base_url = 'http://a/b/c/d;p?q'
        for s, expected in (
            ('g:h', 'g:h'),
            ('g', 'http://a/b/c/g'),
            ('./g', 'http://a/b/c/g'),
            ('g/', 'http://a/b/c/g/'),
            ('/g', 'http://a/g'),
            ('//g', 'http://g/'),  # Slightly different output, trailing /
            ('?y', 'http://a/b/c/d;p?y'),
            ('g?y', 'http://a/b/c/g?y'),
            ('#s', 'http://a/b/c/d;p?q#s'),
            ('g#s', 'http://a/b/c/g#s'),
            ('g?y#s', 'http://a/b/c/g?y#s'),
            (';x', 'http://a/b/c/;x'),
            ('g;x', 'http://a/b/c/g;x'),
            ('g;x?y#s', 'http://a/b/c/g;x?y#s'),
            ('', 'http://a/b/c/d;p?q'),
            ('.', 'http://a/b/c/'),
            ('./', 'http://a/b/c/'),
            ('..', 'http://a/b/'),
            ('../', 'http://a/b/'),
            ('../g', 'http://a/b/g'),
            ('../..', 'http://a/'),
            ('../../', 'http://a/'),
            ('../../g', 'http://a/g'),
            ('/./g', 'http://a/g'),
            ('/../g', 'http://a/g'),
            ('g.', 'http://a/b/c/g.'),
            ('.g', 'http://a/b/c/.g'),
            ('g..', 'http://a/b/c/g..'),
            ('..g', 'http://a/b/c/..g'),
            ('./../g', 'http://a/b/g'),
            ('./g/.', 'http://a/b/c/g/'),
            ('g/./h', 'http://a/b/c/g/h'),
            ('g/../h', 'http://a/b/c/h'),
            ('g;x=1/./y', 'http://a/b/c/g;x=1/y'),
            ('g;x=1/../y', 'http://a/b/c/y'),
            ('g?y/./x', 'http://a/b/c/g?y/./x'),
            ('g?y/../x', 'http://a/b/c/g?y/../x'),
            ('g#s/./x', 'http://a/b/c/g#s/./x'),
            ('g#s/../x', 'http://a/b/c/g#s/../x'),
        ):
            with self.subTest(s=s):
                actual = join_url(base_url, s)
                self.assertEqual(actual, expected)

    def test_join_url_invalid(self):
        for base_url, s in (
            (1, './g'),
            ('https://example.org', 1),
            ('bogus', './g'),
        ):
            with self.subTest(base_url=base_url, s=s):
                with self.assertRaises(ValueError):
                    join_url(base_url, s)

    def test_normalize_url(self):
        for s, expected in (
            ('https://example.org', 'https://example.org/'),
            ('https://example.org/../yolo.txt', 'https://example.org/yolo.txt'),
            ('https://example.org/dir/../yolo.txt', 'https://example.org/yolo.txt'),
            (
                'https://example.org/dir_1/dir_2/../../yolo.txt',
                'https://example.org/yolo.txt',
            ),
            (
                'https://example.org/dir_1/dir_2/../../../yolo.txt',
                'https://example.org/yolo.txt',
            ),
            (
                'https://example.org/dir_1/dir_2/../..//yolo.txt',
                'https://example.org//yolo.txt',
            ),
        ):
            with self.subTest(s=s):
                actual = normalize_url(s)
                self.assertEqual(actual, expected)

    def test_normalize_url_error(self):
        for s in (1, 'bogus'):
            with self.subTest(s=s):
                with self.assertRaises(ValueError):
                    normalize_url(s)

    def test_parse_url(self):
        s = 'https://user_1:password_1@example.org:8080/dir/../api?q=1#frag'
        actual = parse_url(s)
        expected = {
            'href': 'https://user_1:password_1@example.org:8080/api?q=1#frag',
            'username': 'user_1',
            'password': 'password_1',
            'protocol': 'https:',
            'host': 'example.org:8080',
            'port': '8080',
            'hostname': 'example.org',
            'pathname': '/api',
            'search': '?q=1',
            'hash': '#frag',
            'origin': 'https://example.org:8080',
        }
        self.assertEqual(actual, expected)

    def test_parse_url_subset(self):
        s = 'https://user_1:password_1@example.org:8080/dir/../api?q=1#frag'
        actual = parse_url(s, attributes=('username', 'password'))
        expected = {'username': 'user_1', 'password': 'password_1'}
        self.assertEqual(actual, expected)

    def test_parse_url_error(self):
        for s in (1, 'bogus'):
            with self.subTest(s=s):
                with self.assertRaises(ValueError):
                    parse_url(s)

    def test_replace_url(self):
        s = 'https://www.example.org/yolo.txt?q=1#2'
        for kwargs, expected in (
            (
                {'username': 'user', 'password': 'pass'},
                'https://user:pass@www.example.org/yolo.txt?q=1#2',
            ),
            ({'protocol': 'http:'}, 'http://www.example.org/yolo.txt?q=1#2'),
            ({'port': '80'}, 'https://www.example.org:80/yolo.txt?q=1#2'),
            ({'host': 'www.example.com'}, 'https://www.example.com/yolo.txt?q=1#2'),
            ({'hostname': 'example.com'}, 'https://example.com/yolo.txt?q=1#2'),
            ({'search': '?q=0'}, 'https://www.example.org/yolo.txt?q=0#2'),
            ({'hash': '0'}, 'https://www.example.org/yolo.txt?q=1#0'),
        ):
            with self.subTest(kwargs=kwargs):
                actual = replace_url(s, **kwargs)
                self.assertEqual(actual, expected)

    def test_replace_url_error(self):
        for s, kwargs in (
            (1, {}),
            ('bogus', {}),
            ('http://localhost/', {'password': 1}),
            ('http://localhost/', {'hostname': 'exa[mple.org'}),
        ):
            with self.subTest(s=s, kwargs=kwargs):
                with self.assertRaises(ValueError):
                    replace_url(s, **kwargs)
