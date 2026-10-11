import json

import pytest

from workshop.seda import result_passes, verify_bundle


def test_changed_bundle_is_refused(tmp_path):
    (tmp_path/'frozen.json').write_text(json.dumps({'files':{'worker.py':'0'*64}}))
    (tmp_path/'worker.py').write_text('different')
    with pytest.raises(ValueError,match='bundle_mismatch'):
        verify_bundle(tmp_path)


def test_answer_pass_cannot_hide_failed_cleanup():
    report={'cases':[{'passed':True}],'collection_absent':True,'stack_absent':False}
    assert not result_passes(report)


def test_empty_cases_are_not_acceptance():
    assert not result_passes({'cases':[],'collection_absent':True,'stack_absent':True})


def test_explicit_failed_case_is_not_a_pass():
    assert not result_passes({'cases':[{'passed':False}],'collection_absent':True,'stack_absent':True})
