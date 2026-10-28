# Final Project Submission — OnlineCourse

Replace `laxmikant-kadam/OnlineCourse` with the GitHub repository that contains this
project. The line numbers below match the committed version of each file.

> Repository: `https://github.com/laxmikant-kadam/OnlineCourse`

## Task 1 — `models.py` (3 points)

GitHub URL:

```
https://github.com/laxmikant-kadam/OnlineCourse/blob/main/onlinecourse/models.py
```

Local file: `onlinecourse/models.py`

Contains `Question`, `Choice` and `Submission` (plus `Instructor`, `Learner`,
`Course`, `Lesson` and `Enrollment`). `Question.get_score()` evaluates the
selected choices, and `Submission.choices` is a `ManyToManyField` to `Choice`.

## Task 2 — `admin.py` (3 points)

GitHub URL:

```
https://github.com/laxmikant-kadam/OnlineCourse/blob/main/onlinecourse/admin.py
```

Local file: `onlinecourse/admin.py`

Imports seven model classes (`Choice`, `Course`, `Instructor`, `Learner`,
`Lesson`, `Question`, `Submission`) and implements `QuestionInline`,
`ChoiceInline`, `QuestionAdmin`, `LessonAdmin` (also `LessonInline`,
`CourseAdmin` and `ChoiceAdmin`).

## Task 3 — Admin site screenshot (1 point)

Local file: `screenshots/03-admin-site.png`

Shows the **Authentication and Authorization** section and the **OnlineCourse**
section with all registered models.

## Task 4 — `course_details_bootstrap.html` (2 points)

GitHub URL:

```
https://github.com/laxmikant-kadam/OnlineCourse/blob/main/onlinecourse/templates/onlinecourse/course_details_bootstrap.html
```

Local file: `onlinecourse/templates/onlinecourse/course_details_bootstrap.html`

Displays `{{ course.name }}`, loops over `{% for lesson in lessons %}` and uses
Bootstrap cards, buttons and grid classes. Also renders the mock exam form with
`{% for question in questions %}` / `{% for choice in question.choice_set.all %}`.

## Task 5 — `views.py` (2 points)

GitHub URL:

```
https://github.com/laxmikant-kadam/OnlineCourse/blob/main/onlinecourse/views.py
```

Local file: `onlinecourse/views.py`

Contains `submit(request, course_id)` (creates the `Submission`, attaches the
selected choices and redirects to the result page) and
`show_exam_result(request, course_id, submission_id)` (grades the attempt and
renders the results).

## Task 6 — `urls.py` (2 points)

GitHub URL:

```
https://github.com/laxmikant-kadam/OnlineCourse/blob/main/onlinecourse/urls.py
```

Local file: `onlinecourse/urls.py`

Contains:

```python
path("course/<int:course_id>/submit/", views.submit, name="submit"),
path(
    "course/<int:course_id>/submission/<int:submission_id>/result/",
    views.show_exam_result,
    name="show_exam_result",
),
```

## Task 7 — Successful exam screenshot (2 points)

Local file: `screenshots/07-final.png`

Shows the **Congratulations, John!** message, the score **40/40 (100/100)** and
the per-question exam results.

## Demo accounts

| Role | Username | Password |
| --- | --- | --- |
| Admin | `admin` | `Admin@12345` |
| Learner | `john` | `Learner@123` |
