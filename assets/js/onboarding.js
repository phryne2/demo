document.getElementById('onboarding-form').addEventListener('submit', function (event) {
  event.preventDefault();
  const name = document.getElementById('name').value;
  const email = document.getElementById('email').value;
  const goals = document.getElementById('goals').value;

  // Save user data (mock example, replace with backend)
  localStorage.setItem('userData', JSON.stringify({ name, email, goals }));

  window.location.href = './dashboard.html';
});
