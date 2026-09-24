import getpass

from django.contrib import auth
from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError

User = auth.get_user_model()


class Command(BaseCommand):
    help = "Create the bootstrap admin account for this project."

    def add_arguments(self, parser):
        parser.add_argument("--username", dest="username")
        parser.add_argument("--email", dest="email")
        parser.add_argument("--password", dest="password")
        parser.add_argument(
            "--noinput",
            action="store_true",
            help="Do not prompt the user for input. Requires --username, --email, and --password.",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="Create the admin even if a superuser already exists.",
        )

    def handle(self, *args, **options):
        username = options["username"]
        email = options["email"]
        password = options["password"]
        no_input = options["noinput"]
        force = options["force"]

        if not no_input:
            username = username or self._prompt_for_value("Username")
            email = email or self._prompt_for_value("Email")
            if not password:
                password = self._prompt_for_password()
        else:
            if not username or not email or not password:
                raise CommandError("--username, --email, and --password are required when using --noinput.")

        username = (username or "").strip()
        email = (email or "").strip()

        if not username:
            raise CommandError("Username is required.")
        if not email:
            raise CommandError("Email is required.")
        if not password:
            raise CommandError("Password is required.")

        existing_superuser = User.objects.filter(is_superuser=True).order_by("id").first()
        if existing_superuser and not force:
            raise CommandError(
                f"A superuser already exists for this project: {existing_superuser.username}. "
                "Use --force to create another one anyway."
            )

        if User.objects.filter(username__iexact=username).exists():
            raise CommandError(f"A user with the username '{username}' already exists.")

        if User.objects.filter(email__iexact=email).exists():
            raise CommandError(f"A user with the email '{email}' already exists.")

        user = User(username=username, email=email, is_superuser=True, is_staff=True, role=User.ADMIN, must_change_password=False, is_active=True)

        try:
            password_validation.validate_password(password, user=user)
        except ValidationError as exc:
            raise CommandError("Password validation failed: " + "; ".join(exc.messages)) from exc

        if not no_input and not options["password"]:
            confirm_password = self._prompt_for_password("Password confirmation")
            if password != confirm_password:
                raise CommandError("Passwords do not match.")

        user.set_password(password)
        user.save()

        self.stdout.write(
            self.style.SUCCESS(
                f"Created admin account: username={user.username}, email={user.email}, role={user.role}"
            )
        )

    def _prompt_for_value(self, label):
        return input(f"{label}: ")

    def _prompt_for_password(self, label="Password"):
        while True:
            password = getpass.getpass(f"{label}: ")
            if not password:
                self.stderr.write("Password cannot be empty.\n")
                continue
            return password
