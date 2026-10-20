"""Regression/safety checks for the separate offline staging V2. No live Hermes access."""
from __future__ import annotations
import hashlib
import os
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import local_stage_hardened_v2 as h

class PorcelainTests(unittest.TestCase):
    def test_empty(self): self.assertEqual(h._tracked_porcelain_count(b''),0)
    def test_modified(self): self.assertEqual(h._tracked_porcelain_count(b' M file\x00'),1)
    def test_multiple(self): self.assertEqual(h._tracked_porcelain_count(b' M first\x00M  second\x00'),2)
    def test_rename_consumes_two_fields_once(self): self.assertEqual(h._tracked_porcelain_count(b'R  newer\x00older\x00'),1)
    def test_rename_plus_modified(self): self.assertEqual(h._tracked_porcelain_count(b'R  new\x00old\x00 M second\x00'),2)
    def test_copy_consumes_two_fields_once(self): self.assertEqual(h._tracked_porcelain_count(b'C  copy\x00origin\x00'),1)
    def test_missing_nul_fails(self): self.assertRaises(ValueError,h._tracked_porcelain_count,b' M notended')
    def test_missing_rename_source_fails(self): self.assertRaises(ValueError,h._tracked_porcelain_count,b'R  new\x00')
    def test_untracked_refused(self): self.assertRaises(ValueError,h._tracked_porcelain_count,b'?? filename\x00')
    def test_invalid_status_fails(self): self.assertRaises(ValueError,h._tracked_porcelain_count,b'~  filename\x00')

class GitIntegration(unittest.TestCase):
    def setUp(self):
        if not h.shutil.which('git'): self.skipTest('git unavailable')
        self.t=tempfile.TemporaryDirectory();self.addCleanup(self.t.cleanup);self.root=Path(self.t.name)
        for args in (('git','init','-q'),('git','config','user.email','dummy@example.invalid'),('git','config','user.name','Fixture')):
            subprocess.run(args,cwd=self.root,check=True,capture_output=True)
        (self.root/'first.txt').write_text('one')
        subprocess.run(('git','add','first.txt'),cwd=self.root,check=True,capture_output=True)
        subprocess.run(('git','commit','-qm','synthetic'),cwd=self.root,check=True,capture_output=True)
    def test_clean_and_untracked_ignored(self):
        self.assertEqual(h.host_snapshot(self.root)['tracked_dirty_count'],0)
        (self.root/'untracked.txt').write_text('stray')
        self.assertEqual(h.host_snapshot(self.root)['tracked_dirty_count'],0)
    def test_staged_rename_is_one(self):
        subprocess.run(('git','mv','first.txt','renamed.txt'),cwd=self.root,check=True,capture_output=True)
        r=h.host_snapshot(self.root)
        self.assertTrue(r['repo_git_read_ok'])
        self.assertEqual(r['tracked_dirty_count'],1)
        self.assertNotIn('renamed.txt',str(r))
    def test_staged_rename_plus_unstaged_modified_is_one(self):
        subprocess.run(('git','mv','first.txt','renamed.txt'),cwd=self.root,check=True,capture_output=True)
        (self.root/'renamed.txt').write_text('changed')
        self.assertEqual(h.host_snapshot(self.root)['tracked_dirty_count'],1)
    def test_modified_count(self):
        (self.root/'first.txt').write_text('modified')
        self.assertEqual(h.host_snapshot(self.root)['tracked_dirty_count'],1)
    def test_no_side_effects_in_index(self):
        original=(self.root/'.git'/'index').read_bytes()
        h.host_snapshot(self.root)
        self.assertEqual(original,(self.root/'.git'/'index').read_bytes())

class ArchiveTests(unittest.TestCase):
    def setUp(self):
        self.t=tempfile.TemporaryDirectory();self.addCleanup(self.t.cleanup);self.root=Path(self.t.name)
    def mkzip(self, entries):
        file=self.root/'src.zip'
        with zipfile.ZipFile(file,'w') as z:
            for name,content in entries: z.writestr(name,content)
        return file
    def stage(self,z,name='dst'):
        return h.stage_archive(z,h.hash_file(z),self.root/name)
    def test_valid_archive(self):
        z=self.mkzip([('sub/', ''),('sub/file.txt','ok')])
        r=self.stage(z)
        self.assertEqual((self.root/'dst/sub/file.txt').read_text(),'ok')
        self.assertEqual(r['gate'],'NO-GO')
        self.assertEqual((self.root/'dst/STAGING_RECEIPT.json').exists(),True)
    def test_wrong_sha_stops_before_destination(self):
        z=self.mkzip([('a','ok')]); self.assertRaises(ValueError,h.stage_archive,z,'0'*64,self.root/'dst')
        self.assertFalse((self.root/'dst').exists())
    def test_rejects_windows_control_characters(self):
        for name in ('a\x01.txt','a\n.txt','a\r.txt'):
            with self.subTest(name=repr(name)):
                z=self.mkzip([(name,'bad')]);self.assertRaises(ValueError,self.stage,z)
    def test_rejects_windows_extended_reserved_names(self):
        for name in ('CONIN$.txt','CONOUT$.txt','COM¹.txt','LPT³.txt'):
            with self.subTest(name=name):
                z=self.mkzip([(name,'bad')]);self.assertRaises(ValueError,self.stage,z)
    def test_rejects_noncanonical_directory(self):
        z=self.mkzip([('dir////','')]);self.assertRaises(ValueError,self.stage,z)
    def test_rejects_reserved_receipt(self):
        z=self.mkzip([('STAGING_RECEIPT.json','fake')]);self.assertRaises(ValueError,self.stage,z)
    def test_rejects_traversal(self):
        z=self.mkzip([('../escape.txt','bad')]);self.assertRaises(ValueError,self.stage,z)
    def test_rejects_windows_case_collisions(self):
        z=self.mkzip([('A.txt','1'),('a.txt','2')]);self.assertRaises(ValueError,self.stage,z)
    def test_symlink_parent_is_refused(self):
        real=self.root/'real';real.mkdir()
        link=self.root/'linked'
        try:link.symlink_to(real,target_is_directory=True)
        except (OSError,NotImplementedError):self.skipTest('symlinks unavailable')
        z=self.mkzip([('a.txt','ok')]);self.assertRaises(ValueError,h.stage_archive,z,h.hash_file(z),link/'newdir')
        self.assertFalse((real/'newdir').exists())
    def test_broken_symlink_target_refused(self):
        link=self.root/'dangling'
        try:link.symlink_to(self.root/'absent_dir')
        except (OSError,NotImplementedError):self.skipTest('symlinks unavailable')
        z=self.mkzip([('a.txt','ok')]);self.assertRaises(ValueError,h.stage_archive,z,h.hash_file(z),link)
        self.assertFalse((self.root/'absent_dir').exists())
    def test_symlink_archive_refused(self):
        z=self.mkzip([('a.txt','ok')]);link=self.root/'link.zip'
        try:link.symlink_to(z)
        except (OSError,NotImplementedError):self.skipTest('symlinks unavailable')
        self.assertRaises(ValueError,h.stage_archive,link,h.hash_file(z),self.root/'dst')
    def test_large_zip_before_hash(self):
        z=self.mkzip([('a.txt','ok')]);
        with patch.object(h,'MAX_ZIP_BYTES',1):self.assertRaises(ValueError,self.stage,z)
    def test_non_zip_refused_without_destination(self):
        z=self.root/'src.zip';z.write_bytes(b'not-zip')
        self.assertRaises(zipfile.BadZipFile,self.stage,z)
        self.assertFalse((self.root/'dst').exists())
    def test_existing_destination_refused(self):
        z=self.mkzip([('a.txt','ok')]);(self.root/'dst').mkdir()
        self.assertRaises(FileExistsError,self.stage,z)
    def test_no_extraction_on_staged_zip_member_link(self):
        z=self.root/'src.zip'
        info=zipfile.ZipInfo('bad-symlink');info.create_system=3;info.external_attr=(0o120777<<16)
        with zipfile.ZipFile(z,'w') as f:f.writestr(info,'/tmp/secret')
        self.assertRaises(ValueError,self.stage,z)
        self.assertFalse((self.root/'dst').exists())

if __name__=='__main__': unittest.main()
