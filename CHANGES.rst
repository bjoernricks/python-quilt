1.0 (2017-06-30)
================

META
----
 * Changed from LGPLv2.1 to MIT license

FEATURES
--------
 * Added compatibility with Python 3.2-3.6. Now requires Six.
 * quilt/new.py:

   - Added new New class to be able to reuse the cli code in a python
     framework

 * quilt/error.py:

   - Added new PatchAlreadyExists error class

 * quilt/cli:

   - Replaced optparse with argparse.
   - Add "series -v" option.

BUGFIXES
--------
 * quilt/db.py:

   - Check the full ".pc/.version" contents, not just the first byte
   - Fix parsing and error reporting of patch options in series files
   - Fix patch_before to return correct patch. Before the first patch of
     the series has been returned.
   - Always write the ".pc/applied-patches" file with "\n" as newlines,
     rather than using CRLF on Windows with python 3. The trailing CR
     confused the original Quilt in some circumstances.

 * quilt/add.py:

   - Add._backup_file uses file directory for destination directory too
     This fixes creating wrong patches when refreshing a patch for a file
     in a subdirectory of the sources.

 * quilt/utils.py:

   - File.copy create destination directory if it does not exit yet.
     This fixes an issue when importing a patch in a not exiting patches
     directory.
   - TmpFile.file now has read-write access, not just read access
   - Close file descriptors promptly when suppressing child process
     output.

 * quilt/pop.py, quilt/push.py:

   - Fix raising correct exception class.

 * quilt/push.py:

   - Allow pushing a patch even if a previous attempt failed
   - Prevent pushing if the topmost patch needs refreshing first
   - Fix pushing up to a specific patch when some patches are already
     applied.
   - Keep applied patches list consistent if a patch does not apply but
     prior patches were applied, or "push -f" was used

 * quilt/refresh.py

   - Fix filenames in the diff header

 * quit/revert.py:

   - Add missing import for Patch class.
   - Handle when there are multiple files in a patch

 * quilt/delete.py:

   - Choose the first unapplied patch in "delete_next" rather than
     complaining no patches are applied

 * quilt/new.py:

   - The patch created by "new" now becomes the topmost applied patch
     rather then an unapplied patch.

 * quilt/cli/next.py:
   - Fix default behaviour without any patch argument

 * quilt/cli/previous.py:

   - Fix error message when the topmost patch is the first patch
   - Don't report first unapplied patch if no patches are applied

 * quilt/cli/delete.py:

   - Fix passing backup flag to delete_next and delete_patch.

API
---
 * quilt/add.py:

   - Add._backup_file now expects a File class instead of a filename


0.2 (2012-08-31)
================

FEATURES
--------
  * quilt/delete.py:

    - Added Delete class that implements all features of quilt delete

  * quilt/signals.py:

    - Added a signals/slots implementation.

  * quilt/refresh.py:

    - Refresh.refresh refresh now creates a p1 patch and writes an index for
      each changed file. Also it preserves existing patch headers.

  * quilt/revert.py

    - Revert.revert_patch doesn't override source file if it is unchanged

  * quilt/pop.py:

    - Pop._check checks if a refresh file exists if not forced

BUGFIXES
--------
  * quilt.backup.py:

    - Backup.backup_file fix copying a non-empty file

  * quilt.pop.py:

    - Pop.unapply_all and unapply_patch fix for list reverse usage.

  * quilt.revert.py:

    - Revert._file_in_patch and Revert._revert_file fix directory handling
    - Add missing import for Backup class
    - Revert._apply_patch_temporary fix typo in method name
    - Revert._apply_patch_temporary fix setting the correct work dir
    - Revert._apply_patch_temporary fix running patch
    - Revert.revert_file don't delete source file if patch doesn't change
      the file.

  * quilt.utils.py:

    - TmpDirectory.__init__ None values for suffix and prefix are not
      allowed. Use suffix = "" and prefix="temp" as defaults.
    - File.get_directory returns None if the file path doesn't contain a
      directory

API
---
  * quilt/add.py:

    - Add add signal file_added

  * quilt/cli/meta.py:

    - Command.get_cwd add new method to get the current working dir

  * quilt/db.py

    - PatchLines.set_comment new method to set the comment
    - PatchSeries.is_empty add method to check if a series is empty
    - PatchSeries.replace add method to replace a patch in the series
    - InvalidPatchError removed class InvalidPatchError

  * quilt/error.py:

    - AllPatchesApplied.__init__ new constructor that accepts a series and
      optional a top patch.
    - NoPatchesApplied.__init__, NoPatchInSeries.__init__ new constructor
      that expects a series instance.
    - UnknownPatch new class UnknownPatch replaces InvalidPatchError

  * quilt/patch.py:

    - Patch.run new optional parameters quiet and dry_run.
    - Patch.run work_dir and patch_dir are now Direcory parameters
    - Patch.get_header new method to return the header of a patch

  * quilt/pop.py:

    - Pop add new signals empty_patch, unapplying, unapplied_patch and
      unapplied.
    - Pop.unapply_patch, unapply_top_patch, unapply_all added new optional
      param force.

  * quilt/push.py

    - Push add signals applying, applying_patch, applied_patch,
      appllied_empty_patch and applied.
    - Push.apply_all add optional parameters force and quiet

  * quilt/refresh.py:

    - Refresh add signals refreshed and edit_patch.

  * quilt/revert.py:

    - Add add signals file_reverted, file_unchanged

  * quilt/utils.py:

    - TmpFile.write new method to directly write data to the tempfile.
    - Directory.get_name new method to get the name of the directory.
    - Directory.get_absdir new method to get the directory with absolute
      path.
    - Directory.copy new method to recursively copy a directory to a
      destination directory.
    - File.get_absfile new method to get the file with an absulute path
    - File.get_basefile new method to get the file without a path

TESTS
-----
  * tests/test_db.py:

    - Add test for PatchSeries.replace

  * tests/test_push.py

    - Add tests for Push.apply_all and Push.apply_next_patch

  * test/test_pop.py

    - Add tests for Pop.unapply_all and Pop.unapply_top_patch


0.1 (2012-08-16)
================

 * Initial release
