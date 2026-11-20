(function () {
  function calculate(formula, values) {
    const { a, b, c, d } = values;
    if (Object.values(values).some(v => !Number.isFinite(v) || v < 0)) throw new Error('Enter non-negative numbers for every field.');
    if (['percent', 'ratio', 'roi'].includes(formula) && b === 0) throw new Error('The denominator must be greater than zero.');
    if (formula === 'percent' && a > b) throw new Error('The advancing or accepted count cannot exceed the total count.');
    switch (formula) {
      case 'product': return a * b * c * d;
      case 'posting': return a * b + c;
      case 'percent': return a / b * 100;
      case 'average':
        if ([a, b, c].some(v => v > 100)) throw new Error('Use scores between 0 and 100.');
        return (a + b + c) / 3;
      case 'fee': return a * b / 100 * c;
      case 'sum': return a + b + c;
      case 'roi': return (a - b) / b * 100;
      case 'ratio': return a / b;
      default: throw new Error('Unknown calculator.');
    }
  }
  if (typeof module !== 'undefined') module.exports = { calculate };
  if (typeof document === 'undefined') return;
  const form = document.getElementById('resource-calculator');
  if (!form) return;
  form.addEventListener('submit', function (event) {
    event.preventDefault();
    const error = document.getElementById('calculation-error');
    const output = document.getElementById('calculation-result');
    error.textContent = '';
    try {
      const values = Object.fromEntries([...form.querySelectorAll('input')].map(input => [input.name, input.value.trim() === '' ? NaN : Number(input.value)]));
      const result = calculate(form.dataset.formula, values);
      if (!Number.isFinite(result)) throw new Error('The result is too large. Check the input values.');
      output.value = result.toLocaleString(undefined, { maximumFractionDigits: 2 });
    } catch (exception) { error.textContent = exception.message; output.value = 'Unable to calculate'; }
  });
}());
