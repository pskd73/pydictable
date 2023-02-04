cd pydictable
coverage run -m unittest
rm ../reports/coverage/badge.svg
coverage-badge -o ../reports/coverage/badge.svg
rm .coverage
