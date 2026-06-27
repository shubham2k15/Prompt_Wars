import unittest
import uuid

from fastapi.testclient import TestClient

from app.main import app


class MindGardenSmokeTests(unittest.TestCase):
    def test_auth_journal_chat_dashboard_flow(self) -> None:
        with TestClient(app) as client:
            suffix = uuid.uuid4().hex[:8]
            email = f"smoke-{suffix}@example.com"
            register = client.post(
                "/auth/register",
                json={
                    "user_id": f"smoke-user-{suffix}",
                    "email": email,
                    "password": "StrongPass1",
                },
            )
            self.assertEqual(register.status_code, 200)
            tokens = register.json()
            headers = {"Authorization": f"Bearer {tokens['access_token']}"}

            profile = client.patch(
                "/profile",
                headers=headers,
                json={
                    "full_name": "Smoke Test Student",
                    "exam_type": "NEET",
                    "target_rank": "Under 1000",
                    "preferred_language": "English",
                    "motivation_style": "gentle",
                    "communication_style": "empathetic",
                    "study_schedule": {"preferredTime": "Evening"},
                    "wellness_preferences": {"breathing": True},
                },
            )
            self.assertEqual(profile.status_code, 200)

            journal = client.post(
                "/journals",
                headers=headers,
                json={
                    "title": "Stress after revision",
                    "content": "I felt stressed after revision and comparison with friends made me restless.",
                    "mood_self_score": 2,
                    "energy_score": 3,
                    "sleep_hours": 6,
                },
            )
            self.assertEqual(journal.status_code, 200)
            self.assertIn("gentle read of today", journal.json()["ai_summary"].lower())

            session = client.post("/chat/sessions", headers=headers, json={"title": "Smoke test conversation"})
            self.assertEqual(session.status_code, 200)
            session_id = session.json()["id"]

            message = client.post(
                f"/chat/sessions/{session_id}/messages",
                headers=headers,
                json={"content": "I feel burned out about biology and need help focusing."},
            )
            self.assertEqual(message.status_code, 200)

            goal = client.post(
                "/goals",
                headers=headers,
                json={
                    "title": "Complete biology revision",
                    "category": "study",
                    "target_date": "This week",
                    "progress": 20,
                    "status": "in_progress",
                },
            )
            self.assertEqual(goal.status_code, 200)
            goal_id = goal.json()["id"]

            goal_update = client.patch(
                f"/goals/{goal_id}",
                headers=headers,
                json={"progress": 100, "status": "completed"},
            )
            self.assertEqual(goal_update.status_code, 200)
            self.assertEqual(goal_update.json()["status"], "completed")

            habit = client.post(
                "/habits",
                headers=headers,
                json={"name": "Breathing reset", "frequency": "daily", "target_count": 1},
            )
            self.assertEqual(habit.status_code, 200)
            habit_id = habit.json()["id"]

            habit_log = client.post(f"/habits/{habit_id}/logs", headers=headers, json={"status": "done"})
            self.assertEqual(habit_log.status_code, 200)

            dashboard = client.get("/insights/dashboard", headers=headers)
            self.assertEqual(dashboard.status_code, 200)
            self.assertIn("wellness_score", dashboard.json())
            self.assertIn("emotional_timeline", dashboard.json())

            report = client.post("/insights/reports/weekly", headers=headers)
            self.assertEqual(report.status_code, 200)

            export_payload = client.get("/privacy/export", headers=headers)
            self.assertEqual(export_payload.status_code, 200)
            self.assertIn("goals", export_payload.json())

            verification = client.post("/auth/request-verification", json={"email": email})
            self.assertEqual(verification.status_code, 200)
            verification_token = verification.json()["token"]
            verify = client.post("/auth/verify-email", json={"token": verification_token})
            self.assertEqual(verify.status_code, 200)

            forgot = client.post("/auth/forgot-password", json={"email": email})
            self.assertEqual(forgot.status_code, 200)
            reset_token = forgot.json()["token"]
            reset = client.post(
                "/auth/reset-password",
                json={"token": reset_token, "new_password": "StrongerPass2"},
            )
            self.assertEqual(reset.status_code, 200)


if __name__ == "__main__":
    unittest.main()
