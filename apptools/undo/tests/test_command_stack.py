# -----------------------------------------------------------------------------
#
#  Copyright (c) 2015, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in enthought/LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#
#  Thanks for using Enthought open source!
#
# -----------------------------------------------------------------------------

from traits.testing.unittest_tools import unittest
from contextlib import contextmanager
from nose.tools import assert_equal

from apptools.undo.api import CommandStack, UndoManager
from apptools.undo.tests.testing_commands import SimpleCommand, UnnamedCommand


class TestCommandStack(unittest.TestCase):
    def setUp(self):
        self.stack = CommandStack()
        undo_manager = UndoManager()
        self.stack.undo_manager = undo_manager

        self.command = SimpleCommand()

    # Command pushing tests ---------------------------------------------------

    def test_empty_command_stack(self):
        with assert_n_commands_pushed(self.stack, 0):
            pass

    def test_1_command_pushed(self):
        with assert_n_commands_pushed(self.stack, 1):
            self.stack.push(self.command)

    def test_n_command_pushed(self):
        n = 4
        with assert_n_commands_pushed(self.stack, n):
            for i in range(n):
                self.stack.push(self.command)

    # Undo/Redo tests ---------------------------------------------------------

    def test_undo_1_command(self):
        with assert_n_commands_pushed_and_undone(self.stack, 1):
            self.stack.push(self.command)
            self.assertEqual(self.stack.undo_name, self.command.name)
            self.stack.undo()

    def test_undo_n_command(self):
        n = 4
        with assert_n_commands_pushed_and_undone(self.stack, n):
            for i in range(n):
                self.stack.push(self.command)

            for i in range(n):
                self.stack.undo()

    def test_undo_unnamed_command(self):
        unnamed_command = UnnamedCommand()
        with assert_n_commands_pushed(self.stack, 1):
            self.stack.push(unnamed_command)

            # But the command cannot be undone because it has no name
            self.assertEqual(self.stack.undo_name, "")
            # This is a no-op
            self.stack.undo()

    def test_undo_redo_1_command(self):
        with assert_n_commands_pushed(self.stack, 1):
            self.stack.push(self.command)
            self.stack.undo()
            self.stack.redo()

    # Macro tests -------------------------------------------------------------

    def test_define_macro(self):
        with assert_n_commands_pushed(self.stack, 1):
            add_macro(self.stack, num_commands=2)

    def test_undo_macro(self):
        with assert_n_commands_pushed_and_undone(self.stack, 1):
            # The 2 pushes are viewed as 1 command
            add_macro(self.stack, num_commands=2)
            self.stack.undo()

    # Cleanliness tests -------------------------------------------------------

    def test_empty_stack_is_clean(self):
        self.assertTrue(self.stack.clean)

    def test_non_empty_stack_is_dirty(self):
        self.stack.push(self.command)
        self.assertFalse(self.stack.clean)

    def test_make_clean(self):
        # This makes it dirty by default
        self.stack.push(self.command)
        # Make the current tip of the stack clean
        self.stack.clean = True
        self.assertTrue(self.stack.clean)

    def test_make_dirty(self):
        # Start from a clean state:
        self.stack.push(self.command)
        self.stack.clean = True

        self.stack.clean = False
        self.assertFalse(self.stack.clean)

    def test_save_push_undo_is_clean(self):
        self.stack.push(self.command)

        self.stack.clean = True
        self.stack.push(self.command)
        self.stack.undo()
        self.assertTrue(self.stack.clean)

    def test_save_push_save_undo_is_clean(self):
        self.stack.push(self.command)

        self.stack.clean = True
        self.stack.push(self.command)
        self.stack.clean = True
        self.stack.undo()
        self.assertTrue(self.stack.clean)

    def test_push_undo_save_redo_is_dirty(self):
        self.stack.push(self.command)
        self.stack.undo()
        self.stack.clean = True
        self.stack.redo()
        self.assertFalse(self.stack.clean)


def add_macro(stack, num_commands=2):
    command = SimpleCommand()
    stack.begin_macro('Increment n times')
    try:
        for i in range(num_commands):
            stack.push(command)
    finally:
        stack.end_macro()


# Assertion helpers -----------------------------------------------------------

@contextmanager
def assert_n_commands_pushed(stack, n):
    current_length = len(stack._stack)
    yield
    # N commands have been pushed...
    assert_equal(len(stack._stack), current_length+n)
    # ... and the state is at the tip of the stack...
    assert_equal(stack._index, current_length+n-1)


@contextmanager
def assert_n_commands_pushed_and_undone(stack, n):
    current_length = len(stack._stack)
    yield
    # N commands have been pushed and then reverted. The stack still
    # contains the commands...
    assert_equal(len(stack._stack), n)
    # ... but we are back to the initial (clean) state
    assert_equal(stack._index, current_length-1)
