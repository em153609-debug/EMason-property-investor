"""Deterministic guided-workflow navigation helpers, independent of Streamlit."""
STEPS = (
    '1 · Property',
    '2 · Comparable evidence',
    '3 · Renovation',
    '4 · Financing & operations',
    '5 · Investment decision',
    '6 · Save / export',
)
STEP_HELP = (
    'Locate the property, set your offer price and retrieve provider data.',
    'Confirm comparable properties before relying on after-repair value or rent.',
    'Estimate renovation items, contingency and project timeline.',
    'Set financing, property tax, rental expenses and resale assumptions.',
    'Compare BRRRR and Fix & Flip, inspect risk flags and test alternative offers.',
    'Save your analysis privately or export the financial report.',
)

def step_index(label):
    return STEPS.index(label)

def progress_for_step(index):
    if not 0 <= index < len(STEPS):
        raise ValueError('Invalid workflow step')
    return (index + 1) / len(STEPS)

def change_step(state, offset):
    current = state.get('workflow_step', STEPS[0])
    index = step_index(current)
    new_index = min(len(STEPS)-1, max(0,index+offset))
    state['workflow_step'] = STEPS[new_index]
    return STEPS[new_index]

def next_step(state):
    return change_step(state, 1)

def previous_step(state):
    return change_step(state, -1)
