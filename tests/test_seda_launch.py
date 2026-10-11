import hashlib
from pathlib import Path

import pytest

from workshop.launch import verify_launch


def manifest(tmp_path):
    (tmp_path/'host.py').write_text('reviewed')
    return {'image_id':'sha256:'+'1'*64,
            'host_code':{'host.py':hashlib.sha256(b'reviewed').hexdigest()}}


def test_launch_refuses_changed_host_code(tmp_path):
    value=manifest(tmp_path)
    (tmp_path/'host.py').write_text('changed')
    with pytest.raises(ValueError,match='host_code_mismatch'):
        verify_launch(tmp_path,value,value['image_id'])


def test_launch_refuses_unintended_image(tmp_path):
    value=manifest(tmp_path)
    with pytest.raises(ValueError,match='candidate_image_required'):
        verify_launch(tmp_path,value,'sha256:'+'2'*64)


def test_launch_refuses_path_escape(tmp_path):
    value=manifest(tmp_path)
    value['host_code']={'../host.py':'0'*64}
    with pytest.raises(ValueError,match='host_code_mismatch'):
        verify_launch(tmp_path,value,value['image_id'])


def test_launch_accepts_exact_identity(tmp_path):
    value=manifest(tmp_path)
    assert verify_launch(Path(tmp_path),value,value['image_id'])
