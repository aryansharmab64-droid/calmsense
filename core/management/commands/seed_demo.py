import os
import random
import secrets
from datetime import datetime, time, timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from sensors.models import SensorReading, SimulationState
from sensors.services import build_reading
from sensors.simulator import generate_reading
from wellness.models import ActivityLog, Notification, SleepLog

User = get_user_model()

DEMO_DISPLAY_NAME = "Demo Evaluator"
DAY_PLAN = ["relaxed", "busy", "busy", "poor_sleep", "relaxed", "mixed", "busy", "relaxed", "poor_sleep", "mixed"]
# scenario: (mean sleep hours, typical quality 1-5, mean daily steps)
DAY_PROFILE = {
    "relaxed": (7.6, 4, 8500),
    "busy": (6.3, 3, 4800),
    "poor_sleep": (4.8, 2, 5200),
    "mixed": (6.8, 3, 7000),
}


class Command(BaseCommand):
    help = "Create or restore the demonstration account with synthetic history (demo account only)."

    def add_arguments(self, parser):
        parser.add_argument("--username", default="demo")
        parser.add_argument("--days", type=int, default=30)

    def handle(self, *args, **opts):
        username, days = opts["username"], opts["days"]
        if not 1 <= days <= 90:
            raise CommandError("--days must be between 1 and 90.")

        env_password = os.getenv("DEMO_PASSWORD")
        user = User.objects.filter(username=username).first()
        shown_password = None

        if user is None:
            password = env_password or secrets.token_urlsafe(10)
            user = User(username=username, first_name="Demo")
            user.set_password(password)
            user.save()
            user.profile.display_name = DEMO_DISPLAY_NAME
            user.profile.consent_optional_data = True
            user.profile.save()
            shown_password = "(from DEMO_PASSWORD in .env)" if env_password else password
        else:
            if user.profile.display_name != DEMO_DISPLAY_NAME:
                raise CommandError(f"'{username}' exists and is not a demo account. Choose another --username.")
            if env_password:
                user.set_password(env_password)
                user.save()
                shown_password = "(from DEMO_PASSWORD in .env)"

        # Restore: remove only this demo user's synthetic data
        SensorReading.objects.filter(user=user, is_simulated=True).delete()
        SleepLog.objects.filter(user=user, is_simulated=True).delete()
        ActivityLog.objects.filter(user=user, is_simulated=True).delete()
        Notification.objects.filter(user=user).delete()
        SimulationState.objects.filter(user=user).delete()

        rng = random.Random(190)  # reproducible
        today = timezone.localdate()
        now = timezone.now()
        readings, sleep_logs, activity_logs = [], [], []

        for offset in range(days - 1, -1, -1):
            day = today - timedelta(days=offset)
            key = DAY_PLAN[(days - 1 - offset) % len(DAY_PLAN)]
            tick = 0
            for minutes in range(7 * 60, 22 * 60 + 1, 30):
                ts = timezone.make_aware(datetime.combine(day, time(minutes // 60, minutes % 60)))
                if ts > now:
                    break
                payload = generate_reading(key, tick, rng, ts)
                tick += 1
                readings.append(build_reading(user, payload, source="simulation",
                                              is_simulated=True, scenario=key))
            sleep_mean, quality, steps_mean = DAY_PROFILE[key]
            sleep_logs.append(SleepLog(
                user=user, sleep_date=day, is_simulated=True,
                duration_hours=round(max(2.0, min(11.0, rng.gauss(sleep_mean, 0.5))), 1),
                quality=max(1, min(5, quality + rng.choice([-1, 0, 0, 1])))))
            activity_logs.append(ActivityLog(
                user=user, date=day, is_simulated=True,
                steps=max(0, int(rng.gauss(steps_mean, 900))),
                active_minutes=max(0, int(steps_mean / 130 + rng.gauss(0, 6)))))

        SensorReading.objects.bulk_create(readings, batch_size=500, ignore_conflicts=True)
        SleepLog.objects.bulk_create(sleep_logs, ignore_conflicts=True)
        ActivityLog.objects.bulk_create(activity_logs, ignore_conflicts=True)
        Notification.objects.create(
            user=user, kind="system",
            message="Demonstration data loaded. All readings in this account are synthetic.")

        self.stdout.write(self.style.SUCCESS(
            f"Demo data ready: {len(readings)} readings, {len(sleep_logs)} sleep logs, "
            f"{len(activity_logs)} activity logs (all synthetic)."))
        self.stdout.write(f"Username: {username}")
        if shown_password:
            self.stdout.write(f"Password: {shown_password}   (demonstration only)")
        else:
            self.stdout.write("Password: unchanged (set DEMO_PASSWORD in .env to change it).")