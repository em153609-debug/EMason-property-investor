from core.workflow import STEPS, STEP_HELP, step_index, progress_for_step, change_step, next_step, previous_step

def test_stages_and_help_align():
    assert len(STEPS)==len(STEP_HELP)==6
    assert len(set(STEPS))==6

def test_navigation_clamps_at_ends():
    d={'workflow_step':STEPS[0]}
    previous_step(d)
    assert d['workflow_step']==STEPS[0]
    for _ in range(20): next_step(d)
    assert d['workflow_step']==STEPS[-1]
    next_step(d)
    assert d['workflow_step']==STEPS[-1]

def test_back_restores_prior_stage():
    d={'workflow_step':STEPS[2]}
    previous_step(d)
    assert d['workflow_step']==STEPS[1]
    next_step(d)
    assert d['workflow_step']==STEPS[2]

def test_progress():
    assert progress_for_step(0)==1/6
    assert progress_for_step(5)==1

def test_invalid_step():
    import pytest
    with pytest.raises(ValueError): progress_for_step(-1)

def test_index():
    for n,step in enumerate(STEPS): assert step_index(step)==n
