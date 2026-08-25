//Hero background slideshow

const heroSlides = document.querySelectorAll(".hero-slide");

if (heroSlides.length > 1) {
  let current = 0;
  setInterval(function () {
    heroSlides[current].classList.remove("active");
    current = (current + 1) % heroSlides.length;
    heroSlides[current].classList.add("active");
  }, 2000);
}

// Quest Board: live search of session cards by quest title 

const searchInput = document.querySelector("#search-input");

if (searchInput) {
  const sections = document.querySelectorAll(".day-section");

  searchInput.addEventListener("input", function () {
    const searchText = searchInput.value.toLowerCase().trim();

    for (const section of sections) {
      let visibleCards = 0;

      const cards = section.querySelectorAll(".session-card");
      for (const card of cards) {
        const title = card.querySelector(".quest-title").textContent.toLowerCase();
        if (title.includes(searchText)) {
          card.classList.remove("hidden-card");
          visibleCards = visibleCards + 1;
        } else {
          card.classList.add("hidden-card");
        }
      }

      if (visibleCards === 0) {
        section.classList.add("hidden-card");
      } else {
        section.classList.remove("hidden-card");
      }
    }
  });
}

//  Show / hide password on the login and registration forms

const toggleButtons = document.querySelectorAll(".toggle-password");

for (const button of toggleButtons) {
  button.addEventListener("click", function () {
    const field = document.querySelector("#" + button.getAttribute("data-target"));
    const icon = button.querySelector("i");
    if (field.type === "password") {
      field.type = "text";
      icon.classList.remove("bi-eye");
      icon.classList.add("bi-eye-slash");
    } else {
      field.type = "password";
      icon.classList.remove("bi-eye-slash");
      icon.classList.add("bi-eye");
    }
  });
}

//Registration: check that password and confirmation match

const pwField = document.querySelector("#txt_password");
const confirmField = document.querySelector("#txt_confirm_password");
const matchNote = document.querySelector("#password-match");

if (pwField && confirmField && matchNote) {
  function checkMatch() {
    if (confirmField.value === "") {
      matchNote.textContent = "";
      confirmField.setCustomValidity("");
    } else if (pwField.value === confirmField.value) {
      matchNote.textContent = "Passwords match";
      matchNote.classList.remove("counter-full");
      confirmField.setCustomValidity("");
    } else {
      matchNote.textContent = "Passwords do not match";
      matchNote.classList.add("counter-full");
      confirmField.setCustomValidity("The two passwords do not match");
    }
  }

  pwField.addEventListener("input", checkMatch);
  confirmField.addEventListener("input", checkMatch);
}

// New quest: live character counter for the description (max 300)

const descField = document.querySelector("#txt_description");
const descCounter = document.querySelector("#desc-counter");

if (descField && descCounter) {
  const max = parseInt(descCounter.getAttribute("data-max"), 10);

  function updateCounter() {
    const used = descField.value.length;
    descCounter.textContent = used + " / " + max + " characters";
    if (used >= max) {
      descCounter.classList.add("counter-full");
    } else {
      descCounter.classList.remove("counter-full");
    }
  }

  descField.addEventListener("input", updateCounter);
  updateCounter();
}

//Session detail: role select updates remaining and companion rule

const roleSelect = document.querySelector("#role-select");
const placesSelect = document.querySelector("#places-select");
const placesHint = document.querySelector("#places-hint");

function refreshPlacesOptions() {
  const role = roleSelect.value;
  const remainingSpan = document.querySelector("#rem-" + role);

  if (!remainingSpan) {
    return;
  }

  const remaining = parseInt(remainingSpan.textContent, 10);
  const companionOption = placesSelect.querySelector("option[value='2']");

  if (remaining < 2) {
    companionOption.disabled = true;
    placesSelect.value = "1";
    placesHint.textContent = "Only 1 " + role + " place left: you cannot bring a companion.";
  } else {
    companionOption.disabled = false;
    placesHint.textContent = remaining + " " + role + " places are still free.";
  }
}

if (roleSelect && placesSelect) {
  roleSelect.addEventListener("change", refreshPlacesOptions);
  refreshPlacesOptions();
}
