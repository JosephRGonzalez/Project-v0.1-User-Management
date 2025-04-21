from django.core.management.base import BaseCommand
from usr_mgmt_app.models import Unit

COLLEGES_AND_MAJORS = {
    "architecture": {
        "name": "Gerald D. Hines College of Architecture and Design",
        "majors": [
            "Architecture",
            "Environmental Design",
            "Industrial Design",
            "Interior Architecture"
        ]
    },
    "arts": {
        "name": "Kathrine G. McGovern College of the Arts",
        "majors": [
            "Art History",
            "Art",
            "Dance",
            "Music",
            "Theatre"
        ]
    },
    "business": {
        "name": "C.T. Bauer College of Business",
        "majors": [
            "Accounting",
            "Finance",
            "Management Information Systems",
            "Marketing",
            "Supply Chain Management"
        ]
    },
    "education": {
        "name": "College of Education",
        "majors": [
            "Teaching and Learning",
            "Health",
            "Human Development and Family Studies"
        ]
    },
    "engineering": {
        "name": "Cullen College of Engineering",
        "majors": [
            "Biomedical Engineering",
            "Chemical Engineering",
            "Civil Engineering",
            "Computer Engineering",
            "Electrical Engineering",
            "Mechanical Engineering",
            "Petroleum Engineering"
        ]
    },
    "technology": {
        "name": "Technology Division at the Cullen College of Engineering",
        "majors": [
            "Computer Information Systems",
            "Construction Management",
            "Digital Media",
            "Mechanical Engineering Technology"
        ]
    },
    "liberal_arts": {
        "name": "College of Liberal Arts and Social Sciences",
        "majors": [
            "Communication",
            "Economics",
            "English",
            "History",
            "Political Science",
            "Psychology",
            "Sociology"
        ]
    },
    "nsm": {
        "name": "College of Natural Sciences and Mathematics",
        "majors": [
            "Biology",
            "Chemistry",
            "Computer Science",
            "Mathematics",
            "Physics"
        ]
    },
    "nursing": {
        "name": "Andy and Barbara Gessner College of Nursing",
        "majors": ["Nursing"]
    },
    "medicine": {
        "name": "Tilman J. Fertitta Family College of Medicine",
        "majors": ["Medicine"]
    },
    "optometry": {
        "name": "College of Optometry",
        "majors": ["Optometry"]
    },
    "pharmacy": {
        "name": "College of Pharmacy",
        "majors": ["Pharmacy"]
    },
    "hospitality": {
        "name": "Conrad N. Hilton College of Global Hospitality Leadership",
        "majors": ["Hospitality Management"]
    },
    "law": {
        "name": "UH Law Center",
        "majors": ["Law"]
    },
    "social_work": {
        "name": "Graduate College of Social Work",
        "majors": ["Social Work"]
    },
    "public_affairs": {
        "name": "Hobby School of Public Affairs",
        "majors": ["Public Policy"]
    },
    "honors": {
        "name": "The Honors College",
        "majors": ["Interdisciplinary Studies"]
    },
}

class Command(BaseCommand):
    help = "Load UH colleges and their majors into the Unit table"

    def handle(self, *args, **kwargs):
        for code, data in COLLEGES_AND_MAJORS.items():
            college, created = Unit.objects.get_or_create(
                code=code,
                defaults={"name": data["name"], "is_college": True, "parent": None}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Added college: {college.name}"))
            else:
                self.stdout.write(f"College already exists: {college.name}")

            for major in data["majors"]:
                major_code = f"{code}_{major.lower().replace(' ', '_')}"
                major_unit, major_created = Unit.objects.get_or_create(
                    code=major_code,
                    defaults={"name": major, "is_college": False, "parent": college}
                )
                if major_created:
                    self.stdout.write(self.style.SUCCESS(f"  ↳ Added major: {major}"))
                else:
                    self.stdout.write(f"  ↳ Major already exists: {major}")
