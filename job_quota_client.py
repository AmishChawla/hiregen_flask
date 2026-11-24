"""Translate only the backend's structured quota rejection into a form error."""
class JobPostingLimitError(ValueError):
    pass


def raise_job_limit_error(response):
    if response.status_code != 409:
        return
    try:
        detail = response.json().get('detail', {})
    except (ValueError, AttributeError):
        return
    if isinstance(detail, dict) and detail.get('code') == 'active_job_limit_reached':
        raise JobPostingLimitError(detail.get('message') or 'Active job limit reached. Close or unpublish a job, or save a draft.')
