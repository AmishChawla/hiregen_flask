"""Public calculator pages. Calculations run in the browser; no API or database calls."""
from flask import Blueprint, abort, render_template, Response

resource_pages = Blueprint('resource_pages', __name__)
# Fields: input key, label, suggested unit. No financial or hiring recommendation is inferred.
CALCULATORS = {
    'interview-cost-calculator': ('Interview cost calculator', 'Interviewers × hours per interview × hourly cost × interviews.', 'product', [('a','Interviewers','people'),('b','Hours per interview','hours'),('c','Hourly cost per interviewer','currency'),('d','Number of interviews','interviews')], 'Estimated interview cost'),
    'job-posting-cost-calculator': ('Job posting cost calculator', 'Number of paid postings × cost per posting + other posting costs.', 'posting', [('a','Paid postings','postings'),('b','Cost per posting','currency'),('c','Other posting costs','currency')], 'Estimated posting cost'),
    'offer-acceptance-rate': ('Offer acceptance rate calculator', 'Accepted offers ÷ offers made × 100. Use the same reporting period.', 'percent', [('a','Offers accepted','offers'),('b','Offers made','offers')], 'Offer acceptance rate (%)'),
    'quality-of-hire-calculator': ('Quality of hire calculator', 'Average of the three supplied scores. Enter each on the same 0–100 scale. This is a configurable example metric, not an assessment of a candidate.', 'average', [('a','Performance score','0–100'),('b','Retention score','0–100'),('c','Hiring manager satisfaction score','0–100')], 'Average quality score (%)'),
    'recruitment-agency-fee-calculator': ('Recruitment agency fee calculator', 'Annual salary × agency fee percentage ÷ 100 × hires.', 'fee', [('a','Annual salary per hire','currency'),('b','Agency fee','percent'),('c','Number of hires','hires')], 'Estimated agency fees'),
    'recruitment-budget-calculator': ('Recruitment budget calculator', 'Add internal recruiting, external recruiting, and other planned costs. Use one currency and reporting period.', 'sum', [('a','Internal recruiting costs','currency'),('b','External recruiting costs','currency'),('c','Other planned costs','currency')], 'Total planned recruitment budget'),
    'sourcing-channel-roi': ('Sourcing channel ROI calculator', '(Attributed value − channel cost) ÷ channel cost × 100. Supply your own consistent attribution method.', 'roi', [('a','Value attributed to the channel','currency'),('b','Channel cost','currency')], 'Estimated sourcing ROI (%)'),
    'time-to-fill-calculator': ('Time to fill calculator', 'Total calendar days from requisition opening to offer acceptance ÷ filled positions.', 'ratio', [('a','Total days to fill all positions','days'),('b','Positions filled','positions')], 'Average time to fill (days)'),
    'pipeline-conversion-calculator': ('Pipeline conversion calculator', 'Candidates advancing from a stage ÷ candidates entering that stage × 100.', 'percent', [('a','Candidates advancing','candidates'),('b','Candidates entering','candidates')], 'Stage conversion (%)'),
    'cost-of-bad-hire-calculator': ('Cost of a bad hire calculator', 'Add supplied recruiting, onboarding, and separation/replacement costs. This excludes costs you have not entered.', 'sum', [('a','Recruiting costs','currency'),('b','Training and onboarding costs','currency'),('c','Separation and replacement costs','currency')], 'Estimated total cost'),
}

def calculator(slug):
    config = CALCULATORS.get(slug)
    if not config:
        abort(404)
    title, description, formula, fields, result_label = config
    return render_template('resources/calculator.html', title=title, description=description,
                           formula=formula, fields=fields, result_label=result_label)

@resource_pages.get('/headcount-planning-template')
def headcount_planning():
    return render_template('resources/headcount.html')

@resource_pages.get('/resources/headcount-planning.csv')
def headcount_csv():
    return Response('Department,Current headcount,Planned hires,Expected departures,Projected headcount\nExample department,0,0,0,=B2+C2-D2\n',
                    mimetype='text/csv', headers={'Content-Disposition':'attachment; filename=headcount-planning.csv'})

for _slug in CALCULATORS:
    for _prefix in ('/', '/resources/'):
        resource_pages.add_url_rule(_prefix + _slug, endpoint=_slug.replace('-', '_') + ('_resource' if _prefix != '/' else ''),
                                    view_func=calculator, defaults={'slug': _slug})
