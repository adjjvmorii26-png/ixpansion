import unittest
from tempfile import TemporaryDirectory

from resource_jobs import ResourceJobQueue


class ResourceJobQueueTests(unittest.TestCase):
    def test_job_reaches_complete_with_result(self):
        queue = ResourceJobQueue(workers=1, max_pending=2)
        submitted = queue.submit(lambda: {"resource_id": "resource-1"})
        job = submitted
        for _ in range(100):
            job = queue.get(submitted["job_id"])
            if job["status"] == "complete":
                break
        self.assertEqual(job["status"], "complete")
        self.assertEqual(job["result"], {"resource_id": "resource-1"})
        queue.close()

    def test_job_failure_is_bounded_and_does_not_expose_exception(self):
        queue = ResourceJobQueue(workers=1, max_pending=2)

        def fail():
            raise RuntimeError("synthetic secret detail")

        submitted = queue.submit(fail)
        job = submitted
        for _ in range(100):
            job = queue.get(submitted["job_id"])
            if job["status"] == "failed":
                break
        self.assertEqual(job, {"job_id": submitted["job_id"], "status": "failed", "error": "resource collection failed"})
        queue.close()

    def test_completed_job_state_survives_queue_restart(self):
        with TemporaryDirectory() as directory:
            path = f"{directory}/jobs.sqlite3"
            queue = ResourceJobQueue(workers=1, max_pending=2, db_path=path)
            submitted = queue.submit(lambda: {"resource_id": "resource-2"})
            for _ in range(100):
                if queue.get(submitted["job_id"])["status"] == "complete":
                    break
            queue.close()

            restarted = ResourceJobQueue(workers=1, max_pending=2, db_path=path)
            self.assertEqual(
                restarted.get(submitted["job_id"])["result"],
                {"resource_id": "resource-2"},
            )
            restarted.close()