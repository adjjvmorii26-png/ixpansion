import unittest
from html_boundary_ratchet import added_line_map


class AddedLineMapTests(unittest.TestCase):
    def test_tracks_only_added_lines(self):
        diff = """diff --git a/dashboard/a.html b/dashboard/a.html
index 1111111..2222222 100644
--- a/dashboard/a.html
+++ b/dashboard/a.html
@@ -10,2 +10,3 @@
 context
-old line
+new line one
+new line two
@@ -30 +31 @@
-old tail
+new tail
"""
        self.assertEqual(added_line_map(diff), {"dashboard/a.html": {11, 12, 31}})

    def test_new_file_and_deleted_file(self):
        diff = """diff --git a/new.html b/new.html
new file mode 100644
--- /dev/null
+++ b/new.html
@@ -0,0 +1,2 @@
+<div>
+<script>run()</script>
diff --git a/old.html b/old.html
deleted file mode 100644
--- a/old.html
+++ /dev/null
@@ -1 +0,0 @@
-<div>
"""
        self.assertEqual(added_line_map(diff), {"new.html": {1, 2}})


if __name__ == "__main__":
    unittest.main()
