document.addEventListener("DOMContentLoaded", () => {
    const usernameInput = document.getElementById("username");
    const passwordInput = document.getElementById("password");
    const backButton = document.getElementById("back");
    const loginButton = document.getElementById("login");

    usernameInput.addEventListener("keypress", (e) => {
        if (e.key == "Enter") {
            passwordInput.focus();
        }
    });
    passwordInput.addEventListener("keypress", (e) => {
        if (e.key == "Enter") {
            loginButton.click();
        }
    });
    backButton.addEventListener("click", (e) => {
        window.location = "/";
    });
    loginButton.addEventListener("click", (e) => {
        if (usernameInput.value == "" || passwordInput.value == "") return;

        fetch("/api/login", {
            method: "POST",
            body: JSON.stringify({
                username: usernameInput.value,
                password: passwordInput.value
            }),
            headers: {
                "Content-Type": "application/json"
            }
        })
            .then((response) => response.json())
            .then((json) => console.log(json));
    });
});