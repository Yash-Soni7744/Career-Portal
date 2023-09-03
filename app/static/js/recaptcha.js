function submitResponse() {
  grecaptcha.ready(function () {
    grecaptcha
      .execute("6LfTQOgnAAAAAPUKwxk5C_ZQNIi__k7HGTzbi3Yw", { action: "submit" })
      .then(function (token) {
        const alertText = document.getElementById("alert-text");

        var email = document.getElementById("email").value;
        var password = document.getElementById("password").value;

        if (email == "" || password == "") {
          alertText.classList.add("error-text");
          alertText.innerHTML = "Email adress or password is missing";
          return;
        }

        if (!email.includes("@") || !email.includes(".")) {
          alertText.classList.add("error-text");
          alertText.innerHTML = "Email adress is not valid";
          return;
        }

        if (email.split("@")[1] != "krmu.edu.in") {
          alertText.classList.add("error-text");
          alertText.innerHTML =
            "Only university email addresses are allowed";
          return;
        }

        if (password.length < 8) {
          alertText.classList.add("error-text");
          alertText.innerHTML = "Password must be at least 8 characters long";
          return;
        }

        var data = {
          email: email,
          password: password,
          recaptcha_token: token,
        };

        const submitButton = document.getElementById("submit-button");
        const submitButtonText = submitButton.innerHTML;

        submitButton.innerHTML = "Loading...";
        submitButton.disabled = true;

        fetch(window.location.href, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(data),
        })
          .then(function (response) {
            if (response.status == 200) {
              window.location.href = "/dashboard";
            } else {
              response.json().then(function (data) {
                alertText.classList.add("error-text");
                alertText.innerHTML = data.message;
              });
            }
          })
          .catch(function (error) {
            alertText.classList.add("error-text");
            alertText.innerHTML = error;
          })
          .finally(function () {
            submitButton.innerHTML = submitButtonText;
            submitButton.disabled = false;
          });
      });
  });
}
