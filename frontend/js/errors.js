const $ = (id) => document.getElementById(id);

function node(tag, text = '') {
  const result = document.createElement(tag);
  result.textContent = text;
  return result;
}

export function clearErrors() {
  $('errors').hidden = true;
  $('error-list').replaceChildren();
  document.querySelectorAll('.field-error').forEach((element) => element.remove());
  document.querySelectorAll('[aria-invalid]').forEach((element) => {
    element.removeAttribute('aria-invalid');
    element.setAttribute('aria-describedby', element.dataset.description || '');
  });
}

export function showErrors(issues, findTarget) {
  clearErrors();
  $('result').hidden = true;
  $('empty-result').hidden = false;
  $('result-state').textContent = 'No evaluado. Revisa los mensajes.';
  issues.forEach((issue, index) => {
    const target = findTarget(issue.field);
    const item = node('li');
    const link = node('a', issue.message);
    link.href = `#${target.id}`;
    link.addEventListener('click', (event) => {
      event.preventDefault();
      target.focus();
      if (issue.span && target === $('formula')) {
        const offset = (position) => Array.from(target.value).slice(0, position).join('').length;
        target.setSelectionRange(offset(issue.span.start), offset(issue.span.end));
      }
    });
    item.append(link);
    $('error-list').append(item);
    const local = node('p', issue.message);
    local.id = `field-error-${index}`;
    local.className = 'field-error';
    if (!target.hasAttribute('aria-invalid')) target.dataset.description = target.getAttribute('aria-describedby') || '';
    target.setAttribute('aria-invalid', 'true');
    target.setAttribute('aria-describedby', `${target.getAttribute('aria-describedby') || ''} ${local.id}`.trim());
    target.insertAdjacentElement('afterend', local);
  });
  $('errors').hidden = false;
  $('errors').focus();
}
