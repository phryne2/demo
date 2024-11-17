document.addEventListener('DOMContentLoaded', function () {
  const userData = JSON.parse(localStorage.getItem('userData'));
  const userDiv = document.getElementById('user-data');

  if (userData) {
    userDiv.innerHTML = `
      <p>Name: ${userData.name}</p>
      <p>Email: ${userData.email}</p>
      <p>Goals: ${userData.goals}</p>
    `;
  } else {
    userDiv.innerHTML = '<p>No user data found. Please onboard first.</p>';
  }
});
