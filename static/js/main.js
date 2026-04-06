// This keeps alert messages from staying on the screen too long.
document.querySelectorAll('.alert').forEach((alertBox) => {
  setTimeout(() => {
    alertBox.style.opacity = '0';
    alertBox.style.transform = 'translateX(20px)';
    alertBox.style.transition = 'all 0.3s ease';

    setTimeout(() => {
      alertBox.remove();
    }, 300);
  }, 4000);
});

// This gives textareas a little more room as the user types.
document.querySelectorAll('textarea').forEach((field) => {
  field.addEventListener('input', function () {
    this.style.height = 'auto';
    this.style.height = `${Math.min(this.scrollHeight, 200)}px`;
  });
});
