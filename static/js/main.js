// دکمه تغییر تم
const themeToggle = document.createElement('button');
themeToggle.className = 'btn btn-sm btn-outline-light position-fixed bottom-0 end-0 m-3';
themeToggle.textContent = '🌓 تغییر تم';
document.body.appendChild(themeToggle);

themeToggle.addEventListener('click', () => {
  document.body.classList.toggle('bg-light');
  document.body.classList.toggle('text-dark');
  document.body.classList.toggle('bg-dark');
  document.body.classList.toggle('text-light');
});
