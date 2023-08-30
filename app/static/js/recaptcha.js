function submitResponse() {
  grecaptcha.ready(function () {
    grecaptcha
      .execute("6LfTQOgnAAAAAPUKwxk5C_ZQNIi__k7HGTzbi3Yw", { action: "submit" })
      .then(function (token) {
        const alertText = document.getElementById("alert-text");

        var email = document.getElementById("email").value;
        var password = document.getElementById("password").value;

        if (email == "" || password == "") {
          alertText.innerHTML = "Email adress or password is missing";
          alertText.style.display = "block";
          return;
        }

        if (password.length < 8) {
          alertText.innerHTML = "Password must be at least 8 characters long";
          alertText.style.display = "block";
          return;
        }

        if (!email.includes("@") || !email.includes(".")) {
            alertText.innerHTML = "Email adress is not valid";
            alertText.style.display = "block";
            return;
        }

        if (email.split("@")[1] != "krmu.edu.in") {
            alertText.innerHTML = "Only K.R. Mangalam University email addresses are allowed";
            alertText.style.display = "block";
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
                console.log(data);
                alertText.innerHTML = data.message;
                alertText.style.display = "block";
              });
            }
          })
          .catch(function (error) {
            alertText.innerHTML = error;
            alertText.style.display = "block";
          })
          .finally(function () {
            submitButton.innerHTML = submitButtonText;
            submitButton.disabled = false;
          });
      });
  });
}
