const body = document.querySelector('body'),
  sidebar = body.querySelector('nav'),
  toggle = body.querySelector(".toggle"),
  searchBtn = body.querySelector(".search-box"),
  modeSwitch = body.querySelector(".toggle-switch"),
  modeText = body.querySelector(".mode-text");

// Toggle sidebar visibility
toggle.addEventListener("click", () => {
  sidebar.classList.toggle("close");
})

// Show sidebar when search button is clicked
searchBtn.addEventListener("click", () => {
  sidebar.classList.remove("close");
})

// Toggle dark mode and update mode text
modeSwitch.addEventListener("click", () => {
  body.classList.toggle("dark");

  // Update mode text based on the current mode
  if (body.classList.contains("dark")) {
    modeText.innerText = "Modo claro";
  } else {
    modeText.innerText = "Modo escuro";
  }
});