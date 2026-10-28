# OnlineCourse — Django Final Project

A Django implementation of the **OnlineCourse** final project lab. The app supports
user registration/login, course enrollment, lessons, a mock exam built from
`Question`/`Choice` models, exam submissions and automatic result evaluation.

## Project structure

| Path | Purpose |
| --- | --- |
| `myproject/` | Django project settings and root URL configuration |
| `onlinecourse/models.py` | `Instructor`, `Learner`, `Course`, `Lesson`, `Enrollment`, `Question`, `Choice`, `Submission` |
| `onlinecourse/admin.py` | Admin configuration with `QuestionInline`, `ChoiceInline`, `QuestionAdmin`, `LessonAdmin` |
| `onlinecourse/views.py` | Registration/login, course list & details, enrollment, `submit`, `show_exam_result` |
| `onlinecourse/urls.py` | URL routes including `submit` and `show_exam_result` |
| `onlinecourse/templates/onlinecourse/` | Bootstrap templates, including `course_details_bootstrap.html` |
| `screenshots/03-admin-site.png` | Admin site with **Authentication and Authorization** and **OnlineCourse** sections |
| `screenshots/07-final.png` | Successful mock exam attempt with the **Congratulations** message, score and exam results |

## Running the project locally

```bash
# 1. Create and activate a virtual environment (recommended)
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS / Linux

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create the database
python manage.py migrate

# 4. Create the demo users, course, lessons and exam
python seed_data.py

# 5. Start the development server
python manage.py runserver
```

Then open <http://127.0.0.1:8000/>.

### Demo accounts

| Role | Username | Password |
| --- | --- | --- |
| Admin / superuser | `admin` | `Admin@12345` |
| Learner | `john` | `Learner@123` |

The admin site is available at <http://127.0.0.1:8000/admin/>.

## Taking the mock exam

1. Log in as `john`.
2. Open **Django Application Development** from the course list.
3. Click **Take Exam**, select the answers and click **Submit exam**.
4. The result page shows the score and the outcome of every question.

## Regenerating the screenshots

With the development server running:

```bash
pip install selenium
python scripts/capture_screenshots.py
```

The script logs in through the real login pages with headless Chrome and writes
`screenshots/03-admin-site.png` and `screenshots/07-final.png`.

## Tests

```bash
python manage.py test
```

The tests cover the course detail page, exam submission, score calculation,
the congratulations message and result privacy.
