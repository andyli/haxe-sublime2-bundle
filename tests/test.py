import sublime, os, time, sys, subprocess
from functools import partial
from unittest import TestCase
from threading import Timer

version = sublime.version()

if version >= "3000":
    from UnitTesting.unittesting import DeferrableTestCase
else:
    from unittesting import DeferrableTestCase

# path to the Haxe package folder
root_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

subl = os.getenv("SUBL", "subl")

class TestHxml(DeferrableTestCase):
    def setUp(self):
        if not hasattr(self, "window"):
            self.window = sublime.active_window()

    def open_window(self, folder):
        subprocess.Popen([subl, "-n", folder])
        w = None
        while not w:
            w = [w for w in sublime.windows() if folder in w.folders()]
            yield
        yield w[0]

    def assertTrueWait(self, expect, timeout_sec = 5):
        t = time.clock()
        while time.clock() - t < timeout_sec and not expect():
            yield
        self.assertTrue(expect())

    def test_hxml_simple(self):
        hxml_simple_path = os.path.join(root_path, "tests", "projects", "hxml_simple")
        window = None
        for w in self.open_window(hxml_simple_path):
            window = w
            yield

        view = window.open_file(os.path.join(hxml_simple_path, "Main.hx"))

        # syntax should be Haxe
        self.assertTrue("Haxe" in view.settings().get('syntax'))

        output_path = os.path.join(hxml_simple_path, "Main.n")
        if os.path.exists(output_path):
            os.remove(output_path)

        # test build (Command+B and Ctrl+Enter)
        expect = partial(os.path.exists, output_path)
        for cmd in ["build", "haxe_run_build", "haxe_save_all_and_build"]:
            window.run_command(cmd)
            for _ in self.assertTrueWait(expect):
                yield
            os.remove(output_path)

        # clean up
        window.focus_view(view)
        window.run_command("close_file")
        window.run_command("close")
